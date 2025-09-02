# DOCUMENT_TECHNIQUE.md


## PARTIE 1 – Structure du projet

- ./
    - alembic.ini
    - celerybeat-schedule.bak
    - celerybeat-schedule.dat
    - celerybeat-schedule.dir
    - docker-compose.yml
    - DOCUMENT_TECHNIQUE.md
    - readme.py
    - requi.py
    - requirements.txt
    - structure.html
    - alembic/
        - env.py
        - README
        - script.py.mako
        - versions/
            - a941301de845_set_default_friendship_id_to_1_for_null_.py
            - dcb8d0af45c4_ajout_de_friendship_id_dans_.py
            - f8978745654f_modify_unique_constraint_to_url_user_id.py
    - app/
        - celery_config.py
        - celery_worker.py
        - database.py
        - Dockerfile.backend
        - Dockerfile.celery
        - main.py
        - __init__.py
        - crud/
            - rss_article.py
            - rss_feed.py
            - user.py
        - models/
            - associations.py
            - collection.py
            - collection_articles.py
            - collection_feeds.py
            - collection_members.py
            - collection_message.py
            - collection_permission.py
            - comment.py
            - feed_access.py
            - followers.py
            - rss_article.py
            - rss_feed.py
            - user.py
            - __init__.py
        - routes/
            - articles_router.py
            - collection_chat_router.py
            - collection_router.py
            - comment_router.py
            - export_import_router.py
            - feeds_router.py
            - followers_router.py
            - oauth2_router.py
            - reader.py
            - search_router.py
            - users_router.py
            - user_article_router.py
            - user_feed_router.py
        - schemas/
            - chat.py
            - collection.py
            - comment.py
            - feed_access.py
            - followers.py
            - rss_article.py
            - rss_feed.py
            - token.py
            - user.py
        - services/
            - auth.py
            - email.py
            - invitations.py
            - notifications.py
            - permissions.py
            - security.py
        - tasks/
            - update_feed.py
            - __init__.py
    - front/
        - Dockerfile.frontend
        - index.html
        - nginx.conf
        - package-lock.json
        - package.json
        - vite.config.js
        - public/
            - images/
                - github-logo.png
                - google-logo.png
                - Logo_SUPRSS.jpg
                - microsoft-logo.webp
        - src/
            - App.jsx
            - main.jsx
            - components/
                - AddFeedForm.jsx
                - AddFeedToCollectionPage.jsx
                - ArticleCard.jsx
                - CollectionArticles.jsx
                - CollectionChat.jsx
                - CollectionFeeds.jsx
                - CommentSection.jsx
                - CreateCollectionPage.jsx
                - DisplaySettings.jsx
                - Footer.jsx
                - ForgotPassword.jsx
                - FriendList.jsx
                - Header.jsx
                - LoginCallBack.jsx
                - Logout.jsx
                - NavBar.jsx
                - Notifications.jsx
                - PrivateRoute.jsx
                - ResetPassword.jsx
                - UserSearch.jsx
            - pages/
                - ArticleListPage.jsx
                - CollectionIdPage.jsx
                - CollectionsPage.jsx
                - FeedEditPage.jsx
                - FeedsListPage.jsx
                - Home.jsx
                - HomePage.jsx
                - Login.jsx
                - Profile.jsx
                - Register.jsx
            - services/
                - FollowersAPI.js
            - styles/
                - articles.css
                - base.css
                - chat.css
                - collections.css
                - commentaire.css
                - export_import.css
                - feeds.css
                - friendlist.css
                - home.css
                - index.css
                - invitation_form.css
                - logout.css
                - nav_bar.css
                - notifications.css
                - permissions.css
                - profil.css
                - register.css
                - welcome_card.css
    - test_export/
        - auth_test.http
        - rss_export.json
        - test_auth_api.sh

## PARTIE 2 – Docstrings (modules, classes, fonctions)

### Fichier: .\alembic\env.py

### run_migrations_offline
Run migrations in 'offline' mode.

### run_migrations_online
Run migrations in 'online' mode.

### Fichier: .\alembic\versions\a941301de845_set_default_friendship_id_to_1_for_null_.py

### Module
Set default friendship_id to 1 for null values

Revision ID: a941301de845
Revises: dcb8d0af45c4
Create Date: 2025-08-21 14:42:05.500583

### Fichier: .\alembic\versions\dcb8d0af45c4_ajout_de_friendship_id_dans_.py

### Module
Ajout de friendship_id dans notifications

Revision ID: dcb8d0af45c4
Revises: 
Create Date: 2025-08-21 11:58:11.103340

### upgrade
Upgrade schema.

### downgrade
Downgrade schema.

### Fichier: .\alembic\versions\f8978745654f_modify_unique_constraint_to_url_user_id.py

### Module
Modify unique constraint to (url, user_id)

Revision ID: f8978745654f
Revises: a941301de845
Create Date: 2025-08-26 22:20:39.472129

### upgrade
Upgrade schema.

### downgrade
Downgrade schema.

### Fichier: .\app\celery_config.py

### Fichier: .\app\celery_worker.py

### Fichier: .\app\database.py

### Fichier: .\app\main.py

### Fichier: .\app\__init__.py

### Fichier: .\app\crud\rss_article.py

### Fichier: .\app\crud\rss_feed.py

### Fichier: .\app\crud\user.py

### Fichier: .\app\models\associations.py

### Fichier: .\app\models\collection.py

### Fichier: .\app\models\collection_articles.py

### Fichier: .\app\models\collection_feeds.py

### Fichier: .\app\models\collection_members.py

### Fichier: .\app\models\collection_message.py

### Fichier: .\app\models\collection_permission.py

### Fichier: .\app\models\comment.py

### Fichier: .\app\models\feed_access.py

### Fichier: .\app\models\followers.py

### Fichier: .\app\models\rss_article.py

### Fichier: .\app\models\rss_feed.py

### Fichier: .\app\models\user.py

### Fichier: .\app\models\__init__.py

### Fichier: .\app\routes\articles_router.py

### Fichier: .\app\routes\collection_chat_router.py

### Fichier: .\app\routes\collection_router.py

### Fichier: .\app\routes\comment_router.py

### Fichier: .\app\routes\export_import_router.py

### Fichier: .\app\routes\feeds_router.py

### Fichier: .\app\routes\followers_router.py

### Fichier: .\app\routes\oauth2_router.py

### Fichier: .\app\routes\reader.py

### Fichier: .\app\routes\search_router.py

### Fichier: .\app\routes\users_router.py

### Fichier: .\app\routes\user_article_router.py

### Fichier: .\app\routes\user_feed_router.py

### Fichier: .\app\schemas\chat.py

### Fichier: .\app\schemas\collection.py

### Fichier: .\app\schemas\comment.py

### Fichier: .\app\schemas\feed_access.py

### Fichier: .\app\schemas\followers.py

### Fichier: .\app\schemas\rss_article.py

### Fichier: .\app\schemas\rss_feed.py

### Fichier: .\app\schemas\token.py

### Fichier: .\app\schemas\user.py

### Fichier: .\app\services\auth.py

### Fichier: .\app\services\email.py

### Fichier: .\app\services\invitations.py

### get_default_permissions_for_role
Retourne les permissions par défaut selon le rôle.

### invite_user_to_collection
Invite un utilisateur à une collection si l'invitant a les droits.
Ajoute l'utilisateur dans CollectionMember et crée une CollectionPermission.

### Fichier: .\app\services\notifications.py

### Fichier: .\app\services\permissions.py

### get_collection_members_with_permissions
Retourne la liste des membres d'une collection avec leurs permissions et leur rôle.

### Fichier: .\app\services\security.py

### Fichier: .\app\tasks\update_feed.py

### Fichier: .\app\tasks\__init__.py


## PARTIE 3 – Dépendances Python

- alembic==1.16.4
- amqp==5.3.1
- annotated-types==0.7.0
- anyio==4.9.0
- Authlib==1.6.1
- axios==0.4.0
- bcrypt==3.2.0
- billiard==4.2.1
- celery==5.5.3
- certifi==2025.8.3
- cffi==1.17.1
- charset-normalizer==3.4.3
- click==8.2.1
- click-didyoumean==0.3.1
- click-plugins==1.1.1.2
- click-repl==0.3.0
- colorama==0.4.6
- cryptography==45.0.5
- dnspython==2.7.0
- docker==7.1.0
- ecdsa==0.19.1
- email_validator==2.2.0
- fastapi==0.115.14
- fastapi-cli==0.0.8
- fastapi-cloud-cli==0.1.5
- feedparser==6.0.11
- greenlet==3.2.3
- h11==0.16.0
- httpcore==1.0.9
- httptools==0.6.4
- httpx==0.28.1
- idna==3.10
- itsdangerous==2.2.0
- Jinja2==3.1.6
- kombu==5.5.4
- lxml==6.0.0
- Mako==1.3.10
- markdown-it-py==4.0.0
- MarkupSafe==3.0.2
- mdurl==0.1.2
- orjson==3.11.2
- packaging==25.0
- passlib==1.7.4
- prompt_toolkit==3.0.51
- psycopg2-binary==2.9.10
- pyasn1==0.6.1
- pycparser==2.22
- pydantic==2.11.7
- pydantic-extra-types==2.10.5
- pydantic-settings==2.10.1
- pydantic_core==2.33.2
- Pygments==2.19.2
- python-dateutil==2.9.0.post0
- python-dotenv==1.1.1
- python-jose==3.5.0
- python-multipart==0.0.20
- pywin32==311
- PyYAML==6.0.2
- redis==6.4.0
- requests==2.32.4
- rich==14.1.0
- rich-toolkit==0.15.0
- rignore==0.6.4
- rsa==4.9.1
- sentry-sdk==2.35.0
- sgmllib3k==1.0.0
- shellingham==1.5.4
- six==1.17.0
- sniffio==1.3.1
- SQLAlchemy==2.0.42
- starlette==0.46.2
- typer==0.16.1
- typing-inspection==0.4.1
- typing_extensions==4.14.0
- tzdata==2025.2
- ujson==5.10.0
- urllib3==2.5.0
- uvicorn==0.35.0
- vine==5.1.0
- watchfiles==1.1.0
- wcwidth==0.2.13
- websockets==15.0.1

## PARTIE 4 – Configuration Docker & Services

### backend
- Image: .
- Ports: ['8000:8000']
- Dépendances: ['db', 'redis']

### celery
- Image: .
- Ports: []
- Dépendances: ['backend', 'redis']

### redis
- Image: redis:7
- Ports: ['6379:6379']
- Dépendances: []

### db
- Image: postgres:15
- Ports: ['5432:5432']
- Dépendances: []

### frontend
- Image: ./front
- Ports: ['3000:80']
- Dépendances: ['backend']
