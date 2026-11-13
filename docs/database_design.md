# تصميم قاعدة البيانات الأولي

الجداول الحالية: users, artifacts, archaeological_sites, manuscripts, media_files, audit_logs, security_events.

عند استكمال النظام تضاف جداول roles, permissions, user_permissions, reviews, comments, user_sessions, image_assessments, notifications, backups. استخدم Flask-Migrate/Alembic لإدارة تغييرات المخطط بدلاً من الاعتماد على create_all في الإنتاج.
