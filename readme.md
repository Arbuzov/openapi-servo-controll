
pip3 install ./openapi_servo-0.0.2.tar.gz

ln -sf /usr/local/lib/python3.7/dist-packages/openapi_servo_control/servo-control.service /lib/systemd/system/servo-control.service

systemctl enable servo-control

systemctl daemon-reload
