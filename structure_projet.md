# Structure du projet

## .
- .env
- .env.example
- .gitignore
- alembic.ini
- celerybeat-schedule.bak
- celerybeat-schedule.dat
- celerybeat-schedule.dir
- docker-compose.yml
- README.md
- requirements.txt
- structure.py

## alembic
- env.py
- README
- script.py.mako

## alembic\versions
- a941301de845_set_default_friendship_id_to_1_for_null_.py
- dcb8d0af45c4_ajout_de_friendship_id_dans_.py
- f8978745654f_modify_unique_constraint_to_url_user_id.py

## app
- celery_config.py
- celery_worker.py
- database.py
- Dockerfile.backend
- Dockerfile.celery
- main.py
- __init__.py

## app\crud
- rss_article.py
- rss_feed.py
- user.py

## app\models
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

## app\routes
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

## app\schemas
- chat.py
- collection.py
- comment.py
- feed_access.py
- followers.py
- rss_article.py
- rss_feed.py
- token.py
- user.py

## app\services
- auth.py
- email.py
- invitations.py
- notifications.py
- permissions.py
- security.py

## app\tasks
- update_feed.py
- __init__.py

## front
- .env
- .env.example
- Dockerfile.frontend
- index.html
- nginx.conf
- package-lock.json
- package.json
- vite.config.js

## front\dist
- index.html

## front\dist\assets
- index-C89I0cZQ.css
- index-IWY2nyrk.js

## front\dist\images
- github-logo.png
- google-logo.png
- Logo_SUPRSS.jpg
- microsoft-logo.webp

## front\public

## front\public\images
- github-logo.png
- google-logo.png
- Logo_SUPRSS.jpg
- microsoft-logo.webp

## front\src
- App.jsx
- main.jsx

## front\src\components
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

## front\src\pages
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

## front\src\services
- api.js
- FollowersAPI.js

## front\src\styles
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

## test_export
- auth_test.http
- rss_export.json
- test_auth_api.sh





