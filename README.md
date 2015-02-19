# conduit

Web service running on the blimp (currently bare metal, not in a container) that listens to requests and passes them
onto appropriate channels handled by matching plugins:

 - users - called by [blimp-musterroll](https://github.com/cloudfleet/blimp-musterroll) when a new user
 is created on a CloudFleet Blimp to start a [blimp-mailpile](https://github.com/cloudfleet/blimp-mailpile)
 container with the user account data.
