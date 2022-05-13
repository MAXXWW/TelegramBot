import requests
import telebot
import pymysql
import time
import urllib.request
import os


bot = telebot.TeleBot("5298594970:AAFgtJRDk_VMW5VviBs_SMzzJqsJa1UB2dk")

print("Bot Started...")
bot.send_message(963290379, "tes")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, "Selamat datang user\nSilahkan kirim pesan atau file yang akan di broadcast.")


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(
        message, "Berikut ini merupakan beberapa perintah yang dapat digunakan pada Bot ini :\n1. /start -> untuk memulai menjalankan bot kembali\n2. /end -> untuk mengakhiri bot\n3. /bc_text -> untuk melakukan broadcast text\n4. /bc-img -> untuk melakukan broadcast image\n5. /bc-file -> untuk melakukan broadcast file")


@bot.message_handler(commands=['end'])
def send_message(message):
    bot.reply_to(message, "Terimakasih karena telah menggunakan layanan ini.")
    bot.stop_polling()
    print("Bot Ended...")


def connect_db_broadcast():
    conn = pymysql.connect(
        host='sql6.freesqldatabase.com', user='sql6490878', password='GQG6Mu7jZX', db='sql6490878')
    # host='localhost', user='root', password='', db='db_ims')
    return conn

# BC text


@bot.message_handler(commands=['bc-text'])
def bc_text(message):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    print("=======Siap melakukan broadcast Text Message========")
    users = ["963290379", "1360269826"]
    # users = ["963290379"]

    sql_select = "SELECT * FROM tb_outbox WHERE flag_tele=1 AND type='msg'"
    cursor_broadcast.execute(sql_select)
    results = cursor_broadcast.fetchall()

    if(cursor_broadcast.rowcount == 0):
        print("Tidak ada pesan yang ingin dikirim.")
    else:
        for data in results:
            print("***Memulai broadcast dengan pesan = ", data[1])
            for user in users:
                print("Terdapat pesan yang ingin dikirim.")
                print("-----Broadcast Via Tele-----")
                print("Memulai bc kepada " + user)
                message_user = data[1]
                bot.send_message(user, message_user)
                print("- Menungu {} detik".format(1))
                time.sleep(1)

            sql = "UPDATE tb_outbox SET flag_tele = %s WHERE id_outbox = %s"
            val = (2, data[0])
            cursor_broadcast.execute(sql, val)
            db_broadcast.commit()
        print("========Broadcast pesan via Tele SELESAI========")

# BC image


@bot.message_handler(commands=['bc-img'])
def bc_img(message):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    print("=======Siap melakukan broadcast Image========")
    # users = ["963290379"]
    users = ["963290379", "1360269826"]

    sql_select = "SELECT * FROM tb_outbox WHERE flag_tele=1 AND type='image'"
    cursor_broadcast.execute(sql_select)
    results = cursor_broadcast.fetchall()

    if(cursor_broadcast.rowcount == 0):
        print("Tidak ada foto yang ingin dikirim.")
    else:
        for data in results:
            urllib.request.urlretrieve(data[1], "photo.jpg")
            for user in users:
                print("Terdapat foto yang ingin dikirim.")
                print("-----Broadcast Via Tele-----")
                print("Memulai bc kepada " + user)

                photo = open('photo.jpg', 'rb')
                bot.send_photo(
                    user, photo)
                print("- Menungu {} detik".format(1))
                time.sleep(1)

            sql = "UPDATE tb_outbox SET flag_tele = %s WHERE id_outbox = %s"
            val = (2, data[0])
            cursor_broadcast.execute(sql, val)
            db_broadcast.commit()
        print("========Broadcast foto via Tele SELESAI========")


# BC file

@bot.message_handler(commands=['bc-file'])
def bc_file(message):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    print("=======Siap melakukan broadcast File========")
    # users = ["963290379"]
    users = ["963290379", "1360269826"]

    sql_select = "SELECT * FROM tb_outbox WHERE flag_tele=1 AND type='file'"
    cursor_broadcast.execute(sql_select)
    results = cursor_broadcast.fetchall()

    if(cursor_broadcast.rowcount == 0):
        print("Tidak ada file yang ingin dikirim.")
    else:
        for data in results:
            file_name = data[7]
            file_name = file_name.split("/")
            file_name = file_name[0]
            print(file_name)
            urllib.request.urlretrieve(data[1], file_name)
            for user in users:
                print("Memulai bc kepada " + user)
                file = open(file_name, 'rb')
                bot.send_document(user, file)
                print("- Menungu {} detik".format(1))
                time.sleep(1)

            sql = "UPDATE tb_outbox SET flag_tele = %s WHERE id_outbox = %s"
            val = (2, data[0])
            cursor_broadcast.execute(sql, val)
            db_broadcast.commit()
            file.close()
            os.remove(file_name)

        print("========Broadcast file via Tele SELESAI========")


# Handle text


@bot.message_handler(func=lambda message: True)
def save_message(message):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()
    global PESAN
    PESAN = message.text
    print("-----Pesan Broadcast Baru Terdeteksi-----")
    print("User memasukkan pesan broadcast = ", PESAN)
    balas = "Pesan yang ingin anda broadcast = " + PESAN
    bot.reply_to(message, balas)
    print('Menyimpan pesan broadcast kedalam database.')
    sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line,tgl) VALUES (%s, %s, %s, %s, %s,CURDATE())"
    val = (PESAN, "msg", 1, 1, 1)
    cursor_broadcast.execute(sql, val)
    db_broadcast.commit()
    print('-----Selesai-----')

# Handle Photo


@bot.message_handler(content_types=['photo'])
def save_photo(message):
    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    print("-----Foto Broadcast Baru Terdeteksi-----")

    FILE_ID = message.json["photo"][2]["file_id"]
    RES = requests.get(
        "https://api.telegram.org/bot5298594970:AAFgtJRDk_VMW5VviBs_SMzzJqsJa1UB2dk/getFile?file_id=" + FILE_ID)
    RES = RES.json()
    URL = RES["result"]["file_path"]

    file_name = URL.split("/")

    print("User memasukkan foto broadcast " + URL)

    FULL_URL = "https://api.telegram.org/file/bot5298594970:AAFgtJRDk_VMW5VviBs_SMzzJqsJa1UB2dk/" + URL

    print('Menyimpan foto broadcast kedalam database.')

    sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line,tgl, nama_file) VALUES (%s, %s, %s, %s, %s,CURDATE(), %s)"
    val = (FULL_URL, "image", 1, 1, 1, file_name[1])
    cursor_broadcast.execute(sql, val)
    db_broadcast.commit()

    print('-----Selesai-----')

    bot.reply_to(message, "Foto diterima, dan siap di broadcast")

# Handle File


@bot.message_handler(content_types=['document'])
def save_doc(message):

    db_broadcast = connect_db_broadcast()
    cursor_broadcast = db_broadcast.cursor()

    print("-----File Broadcast Baru Terdeteksi-----")

    FILE_ID = message.document.file_id
    RES = requests.get(
        "https://api.telegram.org/bot5298594970:AAFgtJRDk_VMW5VviBs_SMzzJqsJa1UB2dk/getFile?file_id=" + FILE_ID)
    RES = RES.json()
    URL = RES["result"]["file_path"]

    file_name = URL.split("/")

    print("User memasukkan file broadcast = " + URL)

    FULL_URL = "https://api.telegram.org/file/bot5298594970:AAFgtJRDk_VMW5VviBs_SMzzJqsJa1UB2dk/" + URL

    print('Menyimpan File broadcast kedalam database.')

    sql = "INSERT INTO tb_outbox (out_msg, type, flag, flag_tele, flag_line,tgl, nama_file) VALUES (%s, %s, %s, %s, %s,CURDATE(), %s)"
    val = (FULL_URL, "file", 1, 1, 1, file_name[1])
    cursor_broadcast.execute(sql, val)
    db_broadcast.commit()

    print('-----Selesai-----')

    bot.reply_to(message, "File diterima, dan siap di broadcast")


bot.delete_webhook()
bot.message_handler()
bot.polling(none_stop=True)
