from flask import Blueprint
from controllers.ia_chat_controller import resume, chat

# Blueprint to routes
chat_bp = Blueprint('api', __name__, url_prefix='/api')


@chat_bp.route('/resume', methods=['POST'])
def gerenateResume():
    return resume()

@chat_bp.route('/chat', methods=['POST'])
def generateQuestion():
    return chat()
