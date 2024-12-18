from routes.chat_routes import chat_bp

def register_routes(app):
    app.register_blueprint(chat_bp)