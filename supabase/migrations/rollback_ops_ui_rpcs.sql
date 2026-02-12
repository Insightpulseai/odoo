-- Rollback for ops UI RPCs (backups, project settings, upgrade versions)
-- Use only if you're sure nothing depends on these objects yet.

drop function if exists ops.ui_backups(uuid,int,int);
drop function if exists ops.ui_project_settings(uuid);
drop function if exists ops.ui_project_settings_upsert(uuid,jsonb);
drop function if exists ops.ui_project_upgrade_versions(uuid,int,int);

drop table if exists ops.project_upgrade_versions;
drop table if exists ops.project_settings;
drop table if exists ops.backups;
