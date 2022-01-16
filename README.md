# Overview

Share links or text directly from your mobile device's SendTo/Share menu to any specified page (as appended text) inside an Obsidian vault. 

This is not a (browser dependent) web-clipper but a generic way of sending data via a REST endpoint / PUT request into Obsidian.

Note: This software depends on a fully functional setup of https://github.com/vrtmrz/obsidian-livesync !

Usage Examples:
- share links (or any other text) from any mobile devices to your Obsidian vault
- regularely update a given file in your vault with data/text retreived from some Web Service

# Installing the Server

## Requirements

- a self-hosted local server (e.g. a Raspberry Pi or similar) with Docker installed
- or a (self-hosted) public server with Docker installed
- fully functional setup of https://github.com/vrtmrz/obsidian-livesync
  - don't even try without obsidian-livesync working properly in the first place!

### Security aspects on a public server

The provided *docker-compose.yml* puts the service behind a caddy proxy with basic auth enabled.

WITHOUT THIS IN PLACE AND PROPERLY TESTED (AND A CHANGED DEFAULT PASSWORD! - see below) ANYONE COULD SEND ANYTHING INTO YOUR OBSIDIAN VAULT!!!

-> use at your own risk!

## Configuring the Obsidian/CouchDB parameters

Set the appropriate values in *config/CouchDB.yaml*

This file is mounted as volume into the running Docker container and can be changed while the container is running (i.e. no restart required).

## Building the Docker image

```
docker build -t obsreceiver .
```

## Running the Docker image

### Internal Network, no SSL, no authorization

This is the simplest case, the container is hosted on some internal network and doesn't need any SSL and password protection: (make sure that port 8045 is free or pick another port)

```
docker run -d --name obsreceiver --env SERVER_PORT=$OBS_SERVER_PORT -p $OBS_SERVER_PORT:$OBS_SERVER_PORT \
-v /$(pwd)/obsidian_conf:/root/obsidian_conf obsreceiver:latest
```

### External Network/Public host

In this case, a [Caddy proxy](https://github.com/lucaslorentz/caddy-docker-proxy) with automatic SSL certificate generation and basic auth will protect the obsreceiver container:

- adjust *.env* : set OBS_SERVER_DOMAIN to the domain you will be hosting this on
  - -> this domain needs to be publicly accessible
- start the stack with

```
docker-compose up -d
```

(or merge the relevant contents of *docker-compose.yml* into an already existing docker-compose.yml)

The default password as set in .env OBS_SERVER_PASSWORD is obsidian, to change it:

- run:
```
docker exec -it caddy caddy hash-password
```
- copy and paste the generated password into .env OBS_SERVER_PASSWORD and restart the stack

# Calling the Server's endpoint with a GET request

The base URL will either be:

`http://<your-local-server>:8045/`

or

`https://admin:<OBS_SERVER_PASSWORD>@<OBS_SERVER_DOMAIN>/`

OBS_SERVER_PASSWORD and OBS_SERVER_DOMAIN are defined in the docker compose *.env* file

To check if the server is running properly, simply call it like that (without any other parameters), the response should be:
"Call this with a PUT request on /obsput and your content in the body"

## Parameters

- **timestamp** (optional = true|false, default false): prefix the content with a timestamp
- **doc_id** (optional): overrides the document ID as specified in CouchDB.yaml:target_doc_id
- **type** (optional): list|checkbox - prefix the entry with - or - [ ]
- **body**: 
  - either raw: the [HTML URL encoded](https://www.w3schools.com/tags/ref_urlencode.ASP) content to be added to the page
  - or json (with Content-Type header 'application/json'): `{ "data": "<content to be added>"}` - use this for the iOS shortcut, otherwise, the sortcut app will turn the URL into the actual web page!

## Curl

```
curl --location --request PUT '<base-url>/obsput?timestamp=true&doc_id=MyFolder/IncomingData.md&list=true&type=checkbox' \
--header 'Content-Type: text/plain' --data-raw 'Test from cUrl'
```

## Android

The best way to share text from Android is to use [HTTP Request Shortcuts](https://play.google.com/store/apps/details?id=ch.rmy.android.http_shortcuts&hl=de&gl=US)

- define a new shared variable
- define a new shortcut with the above mentioned URL patterns and parameters
- the shortcut will be visible in your Android's Share menu

## iOS

Here's how to create an iOS Shortcut so that a browser-link can be shared into Obsidian: [iOS Shortcut](iOS-Shortcut.md)
