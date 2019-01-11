## Globus Transfer Handler Plugin for Girder/WholeTale

The Globus provider uses the infrasturecture provided by Globus to transfer
files. Globus is a managed transfer service that initiates and supervises
transfers between two GridFTP servers. This implies that the WholeTale
deployment must have some form of GridFTP server running. The Globus provider
automatically manages a Globus Connect Personal Server for this purpose.

Unlike the HTTP provider where the code directly controls what hapens to the
bits of data that come from the server, the Globus provider requires more work
in ensuring proper data isolation and authorization. Specifically, users should
not be able to see or modify other user's data through the GridFTP server used
on the WholeTale deployment.

A rough overview of the way the implementation works is as follows:

* upon receiving a transfer request, the provider ensures that:
    * a functioning Globus Connect Personal Server instance exists. This may
    require the following steps:
        * create a personal endpoint and initialize it (`create_endpoint`
        followed by `globusconnectpersonal -setup...`)
        * record the endpoint id when creating it to avoid creatig a new
        endpoint on each run; the id store is tied to the Globus API client
        ID, so changing the client ID will result in a new endpoint being
        created
        * the server configuration directory is set to
        `~/.WholeTale/<globus-client-id>`
        * start the server (`globusconnectpersonal -start...`)
        * wait for the server to connect to Globus by polling the endpoint
        status until Globus reports the endpoint as connected (`gcp_connected`)
    * a shared endpoint associated with the user requesting the transfer
    exists; if not, one is created on a user-specific sub-directory of the main
    endpoint and an ACL rule is added granting the user owning the transfer RW
    rights to the root directory of the shared endpoint.
* once the above criteria are satisfied, the provider submits a transfer
request from the source to the user shared endpoint
* when Globus reports the transfer as complete, the file is moved to the
actual destination path (in the private storage dir)

The implementation uses one thread per transfer. This is not ideal since most
of the time is spent polling Globus for the transfer status while holding
resources associated with the thread. A more efficient (but possibly more
complex and error-prone) implementation would use a single thread to handle
all transfers.

Refresh tokens are used wherever possible in order to deal with the limited
validity of normal tokens. In general, due to the relatively large time frames
associated with token validity, testing (automated or manual) is unlikely to
immediately catch problems arising from an improper handling of token validity,
so confidence on the correctness of this aspect is lower than for other parts.

The correctness of the solution rests on the assumption that data on shared
endpoints is only accessible to the user with RW rights granted by the ACL
rule. The Globus documentation appears vague around this point in that it
clarifies what the explicit rule does, but not what the implicit rules are.
Through testing, it appears that this is indeed correct: only the user with
the explicit granted rights can see and write to the shared endpoint. Further
checks would be necessary to ensure that the main endpoint cannot be used to
circumvent the rules of the shared endpoints.

### Configuration

`globus_handler` has the following configuration options, exposed through the standard Girder plugin configuration interface:

#### dm.globus_root_path

A directory where that the Globus provider can use as a temporary drop location
for files. Once Globus Online finishes transfering a file to
`<dm.globus_root_path>`, the file is moved to its final destination
(`<dm.private_storage_path>`) using the operating system's defautl move
operation. It is, therefore, recommended that `<dm.globus_root_path>` be
located on the same filesystem as `<dm.private_storage_path>`.

#### dm.globus_gc_dir

A directory containing an unpacked Globus Connect Personal Server (i.e., it
must contain the `globusconnectpersonal` executable).

#### oauth.globus_client_id
#### oauth.globus_client_secret

The Globus provider requires that users be logged in to WholeTale using OAuth
and through Globus. It, therefore, re-uses some of the settings that the OAuth
plugin alrady requires. Specifically, the Globus client id and client secrets
from OAuth are used.
