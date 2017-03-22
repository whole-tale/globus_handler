#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from bson import objectid
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.model_base import AccessControlledModel
from pymongo.collection import ReturnDocument
import time
from girder import events



# This is the long-term item lock model. Locking in this context means
# 'don't delete'
class Lock(AccessControlledModel):
    FIELD_TRANSFER_IN_PROGRESS = 'dm.transferInProgress'
    FIELD_DELETE_IN_PROGRESS = 'dm.deleteInProgress'
    FIELD_LOCK_COUNT = 'dm.lockCount'
    FIELD_CACHED = 'dm.cached'

    def initialize(self):
        self.name = 'lock'
        self.exposeFields(level = AccessType.READ, fields = {'_id', 'userId', 'sessionId', 'itemId', 'ownerId'})
        self.itemModel = Item()

    def validate(self, lock):
        return lock


    def acquireLock(self, user, sessionId, itemId, ownerId = None):
        """
        Adds a new lock to an item.

        :param user: The user initiating the request.
        :type user: dict or None
        :param session: A session associated with the request.
        :type session: Session
        :param itemId: The (Girder) item being locked
        :type itemId: string or ObjectId
        :param ownerId: The entity requesting the lock. If not specified, the session id is used
        :type ownerId: string or ObjectId
        """

        if ownerId == None:
            ownerId = sessionId

        itemId = objectid.ObjectId(itemId)

        lock = {
            '_id': objectid.ObjectId(),
            'userId': user['_id'],
            'sessionId': sessionId,
            'itemId': itemId,
            'ownerId': ownerId
        }

        self.setUserAccess(lock, user = user, level = AccessType.ADMIN)
        lock = self.save(lock)

        self.waitForPendingDelete(itemId)
        print("No pending delete for " + str(itemId))
        if (self.tryLock(user, sessionId, itemId, ownerId)):
            # we own the transfer
            events.trigger('dm.itemLocked',
                info = {'itemId': itemId, 'user': user, 'sessionId': sessionId})
        return lock

    def waitForPendingDelete(self, itemId):
        # In principle, writing ops should happen in a critical section.
        # However, entering a critical section may require an arbitrary
        # amount of time (while downloads happen). This could be implemented
        # using a queue and asynchronous events, but that's too much engineering.
        # Instead, we wait for deletion operations, since they are quick, and
        # implement downloads using a two step: lock the file to prevent its deletion,
        # then poll for transfer status
        done = False
        while not done:
            result = self.itemModel.update(
                query = {'_id': itemId, Lock.FIELD_DELETE_IN_PROGRESS: {'$ne': True}},
                # make sure no deletes can creep in
                update = {'$inc': {Lock.FIELD_LOCK_COUNT: 1}},
                multi = False)
            done = result.matched_count > 0
            if not done:
                time.sleep(0.05)

    def tryLockForDeletion(self, itemId):
        result = self.itemModel.update(
            query = {
                '_id': itemId,
                Lock.FIELD_DELETE_IN_PROGRESS: {'$ne': True},
                Lock.FIELD_LOCK_COUNT: 0
            },
            update = {'$set': {Lock.FIELD_DELETE_IN_PROGRESS: True}},
            multi = False)
        return result.matched_count > 0

    def unlockForDeletion(self, itemId):
        self.itemModel.update(
            query = {'_id': itemId},
            update = {'$set': {Lock.FIELD_DELETE_IN_PROGRESS: False}},
            multi = False)

    def tryLock(self, user, sessionId, itemId, ownerId):
        # Luckily, Mongo updates are atomic
        result = self.itemModel.update(
            query = {
                '_id': itemId,
                Lock.FIELD_TRANSFER_IN_PROGRESS: {'$ne': True},
                Lock.FIELD_CACHED: {'$ne': True}
            },
            update = {
                '$set': {
                    Lock.FIELD_TRANSFER_IN_PROGRESS: True,
                    'dm.transfer.userId': user['_id'],
                    'dm.transfer.sessionId': sessionId,
                }
            },
            multi = False)
        return result.matched_count > 0

    def releaseLock(self, user, lock):
        itemId = lock['itemId']
        self.removeLock(lock)

        if (self.unlock(itemId)):
            events.trigger('dm.itemUnlocked', info=itemId)

    def removeLock(self, lock):
        self.remove(lock)

    def unlock(self, itemId):
        # Need an update that returns the document. Doing an update and
        # then a query kills atomicity
        result = self.itemModel.collection.find_one_and_update(
            filter = {'_id': itemId},
            update = {'$inc': {Lock.FIELD_LOCK_COUNT: -1}},
            projection = [Lock.FIELD_LOCK_COUNT],
            return_document = ReturnDocument.AFTER
        )
        # can't do [FIELD_LOCK_COUNT] unfortunately
        return result['dm']['lockCount'] == 0

    def unlockAll(self, user, session):
        raise Exception('Not yet here')

    def fileDeleted(self, itemId):
        self.itemModel.update(
            query = {'_id': itemId},
            update = {'$set': {Lock.FIELD_CACHED: False, Lock.FIELD_DELETE_IN_PROGRESS: False}},
            multi = False)

    def fileDownloaded(self, info):
        itemId = info['itemId']
        psPath = info['psPath']
        self.itemModel.update(
            query = {'_id': itemId},
            update = {
                '$set': {
                    Lock.FIELD_CACHED: True,
                    Lock.FIELD_TRANSFER_IN_PROGRESS: False,
                    'dm.psPath': psPath
                },
                '$unset': {
                    'dm.transfer.userId': True,
                    'dm.transfer.sessionId': True
                }
            },
            multi = False)

    def listDownloadingItems(self):
        return self.itemModel.find(query = {Lock.FIELD_TRANSFER_IN_PROGRESS: True})