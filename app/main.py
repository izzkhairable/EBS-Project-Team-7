from flask import Flask, render_template
import redis
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/noob")
def noob():
    # redisHost = 'localhost'
    # redisPort = '6379'
    # redisPassword = ''
    # redisDb = 0
    redisHost = 'redis'
    redisPort = '6379'
    redisPassword = 'kPppOZp2hC'
    redisDb = 5   
    r = redis.Redis(host=redisHost, port = redisPort, db=int(redisDb), password=redisPassword, socket_timeout=None, decode_responses=True)
    r.flushall()
    r.lpush('friend', 'john')
    r.lpush('friend', 'mike')

    return render_template("dashboard.html", data=r.lrange('friend', 0, -1))




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
