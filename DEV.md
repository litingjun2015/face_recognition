/*
 * Created on Mon Mar 18 2019
 *
 * Author John (tingjun.li@gmail.com)
 * Copyright (c) 2019 Yunnan CA
 */


## 参考 
### 1 webservice
### 2 recognize_faces_in_pictures.py

vagrant@homestead:~/Code/face_recognition/examples$ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
{
  "face_found_in_image": true,
  "is_picture_of_obama": true
}


result = [
    {
        "code": 1,
        "size": 3,
        "list": {
            "0": {
                "score": "0.07260242",
                "groupid": "yunnanca:tech",
                "userid": "litingjun001"
            },
            "1": {
                "score": "0.06314546",
                "groupid": "yunnanca:tech",
                "userid": "litingjun002"
            },
            "2": {
                "score": "0.0",
                "groupid": "yunnanca:tech",
                "userid": "litingjun003"
            }
        },
        "info": "success"
    }
]

notFoundresult = [
    {
        "code": 1,
        "size": 0,
        "list": {            
        },
        "info": "success"
    }
]