# CeroHumano

## 🚀 Step-by-Step Initialization Guide

### Step 1: Generate IP-Bound SSL Credentials

Create your self-signed certificate parameters directly using standard `openssl`. Replace `192.168.50.70` with your machine's current local Wi-Fi IP address if it changes:

```bash
openssl req -x509 -nodes -days 730 -newkey rsa:2048 \
  -keyout ./certificates/privkey.pem \
  -out ./certificates/fullchain.pem \
  -subj "/CN=192.168.50.70" \
  -addext "subjectAltName = IP:192.168.50.70"
```

### Step 2: Copy environment settings and change them as you need

```bash
cp ./.env.example ./.env
```

### Step 3. Run

```bash
make up
```
