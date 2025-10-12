# 🌐 WebRTC - Complete Basic Theory Guide

## 📖 Overview
**WebRTC (Web Real-Time Communication)** enables **real-time audio, video, and data** communication directly between peers (P2P) without using a central media server.

### Why WebRTC?
- Low-latency, real-time communication.
- Peer-to-peer connection.
- Secure by default (DTLS + SRTP).
- Free and open-source.

---

## ⚙️ Key Components
- **RTCPeerConnection** → Manages peer-to-peer connections.
- **MediaStreamTrack** → Handles video/audio streams.
- **RTCDataChannel** → Allows direct data communication between peers.

---

## 🔑 Core Concepts

### 1. Signaling
The process where peers exchange connection setup details (**SDP** and **ICE candidates**) using WebSocket, HTTP, or another transport method.

### 2. SDP (Session Description Protocol)
Text-based format that describes the connection parameters such as codecs, IPs, ports, and encryption.

Example:
```
v=0
o=- 46117300 2 IN IP4 127.0.0.1
s=-
m=audio 9 UDP/TLS/RTP/SAVPF 111
a=rtpmap:111 opus/48000/2
```

### 3. ICE (Interactive Connectivity Establishment)
A framework to find the best path between peers through **STUN** or **TURN** servers.

### 4. STUN (Session Traversal Utilities for NAT)
Discovers the public IP and port of a peer behind NAT.

### 5. TURN (Traversal Using Relays around NAT)
Used when direct P2P connection fails; relays data through a TURN server.

### 6. RTP (Real-time Transport Protocol)
Carries real-time audio/video packets.

### 7. RTCP (RTP Control Protocol)
Monitors stream quality (delay, packet loss, jitter).

### 8. DTLS (Datagram Transport Layer Security)
Encrypts control and data communication between peers.

### 9. SRTP (Secure Real-time Transport Protocol)
Encrypts the audio/video streams over RTP.

---

## 🔁 WebRTC Connection Flow
1. **Peer A** creates an *offer* (SDP).
2. **Peer B** receives it, creates an *answer* (SDP).
3. Both exchange **ICE candidates** (network info).
4. Once the ICE negotiation completes → connection is established.

```
Peer A ----(Offer/SDP)---> Peer B
Peer A <---(Answer/SDP)--- Peer B
Peer A <===(ICE Candidates)===> Peer B
```

---

## 🧠 Terminology Summary

| Term | Full Form | Description |
|------|------------|-------------|
| **SDP** | Session Description Protocol | Describes codecs, IPs, ports, etc. |
| **ICE** | Interactive Connectivity Establishment | Finds best route between peers |
| **STUN** | Session Traversal Utilities for NAT | Discovers public IP and port |
| **TURN** | Traversal Using Relays around NAT | Relays data when P2P fails |
| **RTP** | Real-time Transport Protocol | Carries media (audio/video) |
| **RTCP** | RTP Control Protocol | Monitors RTP performance |
| **DTLS** | Datagram Transport Layer Security | Encrypts WebRTC data and control |
| **SRTP** | Secure RTP | Encrypts audio/video |
| **NAT** | Network Address Translation | Maps private IPs to public IP |
| **P2P** | Peer-to-Peer | Direct device-to-device communication |

---

## 🧩 Summary
WebRTC = **Real-Time + Peer-to-Peer + Secure + Open Standard**

It powers:
- Video conferencing (Zoom, Google Meet)
- Real-time streaming
- Multiplayer gaming
- IoT camera communication
- AI video processing (Python `aiortc`)

---

## 📚 Learning Resources
- [WebRTC Official Site](https://webrtc.org)
- [WebRTC for the Curious (Free Book)](https://webrtcforthecurious.com)
- [MDN WebRTC Guide](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [aiortc Documentation](https://aiortc.readthedocs.io/en/latest/)
