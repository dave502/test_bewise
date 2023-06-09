<h2 align="center">Задание №2 - Сервис для конвертации файйлов wav формата в mp3</h2>
<h3 align="center"> Инструкции по сборке и использованию</h3>
Сервис состоит из четырёх docker-контейнеров: <br>
<ul>
  <li> <b>wavmp3_backend</b> - Flask-приложение для обработки api команд (http://127.0.0.1:5000) </li>
  <li> <b>wavmp3_db</b> - СУБД Postgres для хранения полученных от web данных (http://127.0.0.1:5432) </li>
  <li> <b>wavmp3_pgadm</b> - PgAdmin4 для удобной работы с db (http://127.0.0.1:8080)</li>
  <li> <b>wavmp3_frontend</b> - frontend клиент для удобства эусплуатации сервиса (http://127.0.0.1:3001)</li>
</ul>

В каталоге проекта имеется файл Makefile. Процесс сборки и другие опреации с контейнерами можно выполнять посредством обращения к нему с помощью утилиты make. <br>
<h4 align="center">Основные команды для операций с образом приложения</h4>
<ul>
  <li/><b>make up</b> - развернуть сервис
  <li/><b>make down</b> - остановить сервис, удалить контейнера, тома не удалять
  <li/><b>make destroy</b> - остановить сервис, удалить контейнера вместо с томами
  <li/><b>make build</b> - создать образы
  <li/><b>db-shell</b> - запустить psql для bd
  <li/><b>make logs</b> - посмотреть логи запущенных контейнеров
  <li/><b>make help</b> - вывести список доступных команд
  <li/><b>make test</b> - выполнить запросы сервису для проверки его работы
 </ul>

Можно обойтись без использования утилиты make, просто выполнив соответствующие команды из файла Makefile. <br><br>
Как было уже указано выше, для выполнения запроса к сервису, следует выполнить команду ```$ make test```, при этом будет выполнен скрипт <b>/test/test_send_file.py</b> со следующими операциями:
<ol>
<li/> Проверка есть ли сохранённый пользователь в json-файле (сохраняется при первом запуске скрипта для последующих запросов от имени этого пользователя)
<li/> Если пользователь уже сохранён, берутся из файла его уникальное имя и uuid; если запросов ещё не было, выполняется обращение к сервису по ссылке<br>
http://127.0.0.1:5000/api/signup/test_user,<br> после чего сервис создаёт пользователя с уникальным именем и возвращает его имя и uuid, которые сохраняются в json файле (если volume базы данных будет удалён, перед последующим запуском скрипта файл test/test_user_file.json необходимо удалить вручную, т.к. тестовый скрипт будет обращаться к сервису от имени несуществующего пользователя)
<li/> Выполняется запрос по адресу http://127.0.0.1:5000/api/convert, в теле запроса отправляются авторизационные данные и файл для конвертации (файл случайно выбирается из каталога test/wav_samples)
<li/> wav файл сохраняется на сервере в каталоге /uploads/wav, конвертируется (после конвертации файл удаляется) и в формате mp3 сохраняется в каталоге сервера /uploads/mp3
<li/>клиенту возвращается ссылка на сконвертированный файл приблизительного вида http://127.0.0.1:5000/api/record?id=1&user=test_user
<li/> Выполняется запрос по полученной ссылке и сохраняется mp3 файл в каталоге /test/mp3
<li/> После скачивания файла mp3, он удаляется с сервера (чтобы не удалять файл, можно изменить константу REMOVE_AFTER_DOWNLOADING = True в файле routes.py)
</ol>


<h4>Таким образом, чтобы развернуть сервис и выполнить тест, следует выполнить в корневом каталоге следующие команды:</h4>
  <ol>
    <li/> <b>make up</b>
    <li/> <b>make test</b>
  </ol>
<i>Перед выполнением ```make test``` можно выполнить ```make logs```, чтобы убедиться, что все контейнера загружены </i>

Для проверки сервиса в реальной работе можно также воспользоваться frontend приложением по адресу <http://127.0.0.1:3001>. Его интерфейс и функционал интуитивно понятны. Запросы от него передаются flask-приложению по адресу <http://127.0.0.1:5000>

Для использования pgadmin4, необходимо авторизоваться по адресу <http://127.0.0.1:8080> используя следующие данные: <br>
            логин: <admin@admin.com> <br>
            пароль: admin <br>
Затем добавить новый сервер с параметрами <br>
  Host name / address : pgadm_bewise<br>
  User : postgres<br>
  Password : postgres<br>

<h4 align="center">Пример запроса из командной строки:</h4>
\# развёртывание сервиса<br>
<code>make up</code><br>
...<br>
\# посмотреть логи<br>
<code>make logs</code><br>
...<br>
\# Выполнение команды запроса<br>
<code>make test</code><br>
\# Ответ:<br>
<code>
File "sample-15s.wav" will be sent<br>
Link for download file_url='http://127.0.0.1:5000/api/record?id=1&user=test_user' <br>
file "sample-15s.mp3" was received<br>
</code><br>

<h4 align="center">Примечания по проекту</h4>
<ol>
<li/>mp3 файлы идентифицируются в базе по uuid владельца и unix timestamp их создания; изначально я упустил информацию о создании уникального uuid для аудиозаписей, потом переделывать не стал, т.к. вариант с timestamp более практичный.
<li/>в ссылке на mp3 файл в качестве id пользователя используется его уникальное имя, что, в общем-то, не противоречит условию.
</ol>
