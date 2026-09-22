# Video sharing platform API.

### Project technology stack and features

* ⚡️ [FastAPI](https://fastapi.tiangolo.com/) - Python backend API.
* 🐘 [PostgreSQL](https://www.postgresql.org/) - SQL database.
* 💾 [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL database interactions (ORM).
* 📜 [Alembic](https://alembic.sqlalchemy.org/en/latest/) - database migrations.
* 🚀 [Redis](https://redis.io/) - key-value storage and caching.
* 📝 [Taskiq](https://taskiq-python.github.io/) - task queuing and scheduling.
* 🐳 [Docker Compose](https://www.docker.com/) - development and production deployment.
* ✅ [Pytest](https://docs.pytest.org/en/stable/) - testing.
* 📫 Email based password recovery.
* 🔒 Secure password hashing by default.
* 🔑 JWT (JSON Web Token) authentication.

*<u>Note: the list above contains not all but the key items only</u>*


### TODOs:

#### Auth
- [x] Register and Login with password
- [ ] Register and Login with email code
- [x] Account activation
- [x] Logout logic
- [x] JWT tokens whitelist
- [x] Password update and reset
- [x] Email update logic

#### OAuth2
- [x] OAuth2 Register and Login

#### Channels
- [x] CRUD channel
- [x] Channel avatar uploading

#### Subscriptions
- [x] Subscribe to channel
- [x] Unsubscribe from channel
- [x] Get subscribers and subscriptions

#### Videos
- [x] Videos CRUD
- [x] Videos Uploads
- [x] Video CRUD Reactions
- [x] Video CRUD Views
- [x] Video CRUD Comments and Replies
- [x] Video CRUD Comment Reactions

#### Video History
- [x] History CRUD

#### Video Playlists
- [x] Playlists CRUD

#### Posts
- [x] Posts CRUD
- [x] Post Reactions CRUD
- [x] Post Comments and Replies CRUD
- [x] Post Comment Reactions CRUD

#### Reports
- [ ] Video Reports
- [ ] Comments Reports
- [ ] Posts Reports
- [ ] Channel Reports

#### Payments
- [ ] Payments logic
- [ ] Subscription tiers logic
