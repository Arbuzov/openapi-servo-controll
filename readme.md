
pip3 install ./openapi_servo-0.0.2.tar.gz

ln -sf /usr/local/lib/python3.7/dist-packages/openapi_servo_control/servo-control.service /lib/systemd/system/servo-control.service

systemctl enable servo-control

systemctl daemon-reload

## Running the service

Install package dependencies and start the controller:

```bash
pip install aiohttp aiohttp_swagger aiohttp_cors Adafruit_PCA9685
python -m openapi_servo_control
```

Swagger API documentation will be available at `http://localhost:3001/api/docs`.
The REST API now supports setting and reading the movement speed for each axis using
`/api/servo/{axis}/speed/{speed}` and `/api/servo/{axis}/speed`.
