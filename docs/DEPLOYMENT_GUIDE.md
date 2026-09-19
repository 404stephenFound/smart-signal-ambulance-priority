# 🚀 AWS Production Deployment Guide
**Team infinity — First Commit Hackathon (WeMakeDevs × AWS)**

This guide walks you through deploying the **Intelligent Ambulance Priority and Real-Time Traffic Signal Management System** to AWS.

---

## 🌟 Quick Overview of AWS Components
1. **Amazon EC2 (`t3.micro` / `t2.micro` - Free Tier)**: Runs the Dockerized FastAPI backend & WebSocket service.
2. **Amazon CloudFront**: Sits in front of EC2 to provide free HTTPS / WSS (`https://xxxx.cloudfront.net`), enabling browser Geolocation API access on mobile phones.
3. **AWS IoT Core (Region: `ap-south-1` Mumbai)**: Managed MQTT broker with X.509 mutual TLS for ambulances, ESP32 microcontrollers, and edge nodes.

---

## ⚡ Method 1: 5-Minute EC2 Console Deployment (Easiest)

### Step 1: Launch an EC2 Instance
1. Log into your [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **EC2** $\to$ Click **Launch Instance**.
3. **Name:** `Ambulance-Priority-Server`
4. **OS Image:** Select **Ubuntu** (Ubuntu Server 22.04 LTS or 24.04 LTS, Free Tier eligible).
5. **Instance Type:** `t3.micro` (or `t2.micro`).
6. **Key Pair:** Select your key pair or proceed without key pair (you can use EC2 Instance Connect).
7. **Network Settings / Security Group:**
   - Check **Allow SSH traffic from Anywhere** (`22`).
   - Check **Allow HTTP traffic from the internet** (`80`).
   - Click **Edit** $\to$ Add a Custom TCP Rule:
     * **Port Range:** `8000`
     * **Source:** `0.0.0.0/0` (Anywhere)

---

### Step 2: Add UserData Script (Automated Launch)
Under **Advanced Details** $\to$ Scroll down to **User data** $\to$ Paste this script:

```bash
#!/bin/bash
apt-get update -y
apt-get install -y docker.io docker-compose git
systemctl enable docker
systemctl start docker

cd /home/ubuntu
git clone https://github.com/404stephenFound/smart-signal-ambulance-priority.git
cd smart-signal-ambulance-priority
docker-compose up -d --build
```

Click **Launch Instance**.

---

### Step 3: Access Your Live System!
Wait ~2 minutes for initialization. In the EC2 console, copy your **Public IPv4 address** (e.g. `13.233.xx.xx`):

* **Police Command Center Dashboard:**  
  `http://<YOUR_EC2_PUBLIC_IP>:8000`
* **Ambulance Driver HUD:**  
  `http://<YOUR_EC2_PUBLIC_IP>:8000/ambulance`
* **Swagger API Docs:**  
  `http://<YOUR_EC2_PUBLIC_IP>:8000/docs`

---

## 🔒 Step 4: Add Amazon CloudFront for Free HTTPS / WSS
*(Required for mobile phone GPS tracking via HTML5 Geolocation API)*

1. In the AWS Console, search for **CloudFront** $\to$ Click **Create Distribution**.
2. **Origin Domain:** Paste your EC2 Public DNS or IP (e.g. `ec2-13-233-xx-xx.ap-south-1.compute.amazonaws.com`).
3. **Protocol:** Select **HTTP only** (Port `8000` or `80`).
4. **Cache Behavior:**
   * **Allowed HTTP methods:** `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`.
   * **Cache Policy:** Choose `CachingDisabled` (since this is a real-time WebSocket dashboard).
   * **Origin Request Policy:** Choose `AllViewerAndCloudFrontHeaders-2022-06` (forwards WebSocket upgrade headers).
5. Click **Create Distribution**.
6. Once deployed, your public URL will be:  
   👉 `https://dXXXXXXXXX.cloudfront.net`

---

## 📡 Step 5: Connecting to AWS IoT Core (MQTT)

1. In AWS Console, go to **AWS IoT Core** $\to$ **Manage** $\to$ **Things**.
2. Click **Create Things** $\to$ Name: `ambulance_A102` $\to$ Download the generated:
   * Device Certificate (`xxxx-certificate.pem.crt`)
   * Private Key (`xxxx-private.pem.key`)
   * Amazon Root CA 1 (`AmazonRootCA1.pem`)
3. Attach an IoT Policy granting publish/subscribe access on `ambulance/+/telemetry` and `junction/+/command`.
4. Copy your IoT Core ATS endpoint from **Settings** (e.g. `xxxx-ats.iot.ap-south-1.amazonaws.com`).
5. On your server, place the certificates in a `certs/` folder and update `.env`.

---

## 🛠️ Verification & Troubleshooting
To check container status or view live logs on your EC2 instance:
```bash
sudo docker ps
sudo docker logs -f ambulance_priority_backend
```
