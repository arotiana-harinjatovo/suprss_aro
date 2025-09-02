#!/bin/bash

# 1. Register a new user
echo "Registering user..."
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=motdepasse123"
echo -e "\n"

# 2. Get JWT token
echo "Getting JWT token..."
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=motdepasse123" | jq -r '.access_token')
echo "Token: $TOKEN"
echo -e "\n"

# 3. Access protected route /me
echo "Accessing protected route /me..."
curl -X GET http://127.0.0.1:8000/me \
  -H "Authorization: Bearer $TOKEN"
echo -e "\n"

# 4. List registered users
echo "Listing registered users..."
curl -X GET http://127.0.0.1:8000/users
echo -e "\n"
