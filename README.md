# doorlock

## Removed Proprietary Bits

This is a project I had worked on throughout 2018.

**I was given permission to post this** by the company that owns the face recognition technology in the project, so long as all proprietary bits are removed. For the sake of my privacy, I also replaced all mentions of the name of the company with variations of "RedactedCompanyName" and "rcn". All the code & assets in this repository are either from my own work or from the Internet.

## What is this?

A door lock that's controlled by your phone, and unlocks once it sees the face of a registered user. The face recognition functionality was achieved using the company's face recognition API. + a license server

None of this will compile or run properly without the library (except the license server). The purpose of this repo is merely to showcase something that I had worked on.

## Topology

There are 3 folders inside this repository.

In short, **InterRouter** = server, **InterStation** = door lock, **InterStellar** = phone app, **PyRedactedCompanyName** = wrapper for the native library.

### InterRouter

The Station/door lock runs on cellular data, which generally does not support port forwarding, or static IP addresses. For this reason, a third party is required in order to transmit data between a station and a Client (e.g. user's phone). In order to circumvent this, we have a Server (InterRouter) which keeps an open socket to all Stations.

Client->Station data is transmitted by sending a REST request from the Client to the Server, which the server then transmits to the Station via the open socket.
Station->Client data is transmitted from the Station to the Server via the socket, then the Server sends a Push notification to the Client via Firebase.

### PyRedactedCompanyName

I had to build a wrapper for the API, which is compiled as a shared object. It uses ctypes to access the native C functions.

### InterStation

This is the code that's meant to run on the Station computer (Raspi). It handles interfacing with the door lock via GPIO, listening to the camera & processing using the face recognition API, and ideally anything that should be handled on that side of the system.

### InterStellar

The app that runs on users phones. It is used to register new users, add faces, remote control, and watch a live stream from the door on the camera.

### license-server

Not completely related to the door lock, this is a license server built in Node. README.md inside
