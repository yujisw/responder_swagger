# responder_swagger
Schema Driven Development with responder &amp; swagger in python

## 立ち上げ
```
docker-compose up -d nginx
```

## 顔認識
Access to http://0.0.0.0/recognizer
or  
use curl command
```
curl -X POST -F file=@./images/test/kamiki.jpg http://localhost/recognizer
```

## 顔登録
Access to http://0.0.0.0/register
or  
use curl command
```
curl -X POST -F file=@./images/test/kamiki.jpg -F name="kamiki2" http://localhost/register
```

## 登録済み画像
- 場所: images/sample/以下
- 形式: [登録した名前].jpg