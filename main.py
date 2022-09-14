import logging

from flask import Flask, request, Response, render_template, session, redirect, url_for
from waitress import serve


from src.qrCodeHelper import generate_qr_files
from src.dbHelper import create_table, get_uuid_status, get_status_by_char, change_uuid_status
from src.webHelper import ticket_status_to_text
import config


#  @ToDo: configure flask logger to write one line exceptions
app = Flask(__name__)
app.secret_key = config.COOKIES_KEY
logging.basicConfig(format='%(asctime)s:%(filename)s:%(levelname)s %(funcName)s: %(message)s', level=logging.INFO, filename=config.LOG_PATH)
logger = logging.getLogger('qrcodeTicket')


def log(_log_level: str, msg: str):
    """
    Convert multiline log to one line log

    :param _log_level: UNIX-type log level in string
    :param msg: Logging message
    :return:
    """
    msg = str(msg).replace('\n', '\\n')
    if 'error' == _log_level:
        logger.error(msg)
    elif 'info' == _log_level:
        logger.info(msg)
    elif 'warning' == _log_level:
        logger.warning(msg)
    elif 'exception' == _log_level:
        logger.exception(msg)
    else:
        logger.debug(msg)


'''
@app.route('/receive_data')
def get_id():
    the_id = request.args.get('button_id')
    return "<p>Got it!</p>"
'''


def logged_user_login():
    for user_login in config.VALIDATORS_LIST:
        if 'username' in session.keys():
            if user_login == session['username']:
                return user_login
    return False


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session['username'] = None
        return redirect(url_for('root_path'))
    elif request.method == 'GET':
        return f'''
                        <form method="post">
                            <p><input type=text name=username value='{session['username']}'>
                            <p><input type=submit value=Logout>
                        </form>
        '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        for _id, user_login in enumerate(config.VALIDATORS_LIST):
            if user_login == request.form['username']:
                if request.form['password'] == config.VALIDATORS_PASS_LIST[_id]:
                    session['username'] = user_login
                    break
        return redirect(url_for('root_path'))
    elif request.method == 'GET':
        return '''
                <form method="post">
                    <p><input type=text name=username>
                    <p><input type=text name=password>
                    <p><input type=submit value=Login>
                </form>
            '''


@app.route('/', methods=['GET', 'POST'])
def root_path():
    if request.method == 'POST':
        result_status = change_uuid_status(request.form['uuid'], request.form['dropdown'], session['username'])
        if not result_status:
            return '''<p>Error changing status.</p>'''
        return '''<p>Status changed successfully.</p>'''
    elif request.method == 'GET':
        logged_username = logged_user_login()
        get_data = request.args.to_dict()
        uuid_val = get_data.get('t', None)
        if uuid_val is not None and logged_username is not False:
            uuid_val = uuid_val.replace("'", '')
            cur_status = get_uuid_status(uuid_val)
            class_name, status_text = ticket_status_to_text(get_status_by_char(cur_status))
            return render_template('validateTicket.html', logged_username=logged_username, status_class=class_name,
                                   status_text=status_text, uuid=uuid_val)
        else:
            return render_template('fish.html', logged_username=logged_username)


@app.route('/generateQRCodes', methods=['GET'])
def generate_qrcodes():
    get_data = request.args.to_dict()
    if config.GENERATION_CODE == get_data.get('code', None):
        generate_qr_files(count=config.QRCODES_COUNT, file_path=config.QRCODES_PATH, file_prefix=config.QRCODE_FILE_PREFIX)
        return '''<p>Generation complete.</p>'''
    return redirect(url_for('root_path'))


@app.errorhandler(Exception)
def exception_logger(error):
    """
    Flask exception hook

    :param error: error message
    :return: Response message
    """
    log('exception', str(error))
    return str(error)


def create_app():
    """
    Function to run Flask as service

    :return: Flask instance
    """
    try:
        serve(app, host='0.0.0.0', port=config.PORT)
    except Exception as _ex:
        log('exception', str(_ex))
    return app


if __name__ == '__main__':
    """
    Code for debug run
    """
    try:
        create_table(config.DB_UUID_TABLE_NAME)
        app.run(host='0.0.0.0', port=config.PORT)
    except Exception as _e:
        log('exception', str(_e))
