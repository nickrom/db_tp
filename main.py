from db_app import app
from db_app.user_app.user_app import app as user_app
from db_app.forum_app.forum_app import app as forum_app
from db_app.thread_app.thread_app import app as thread_app
from db_app.post_app.post_app import app as post_app
from db_app.common_app.common_app import app as common_app

API_PREFIX = "/db/api"

app.register_blueprint(common_app, url_prefix=API_PREFIX)
app.register_blueprint(user_app, url_prefix=API_PREFIX + '/user')
app.register_blueprint(forum_app, url_prefix=API_PREFIX + '/forum')
app.register_blueprint(thread_app, url_prefix=API_PREFIX + '/thread')
app.register_blueprint(post_app, url_prefix=API_PREFIX + '/post')

app.run()
