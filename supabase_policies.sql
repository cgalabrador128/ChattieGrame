-- Enable Row Level Security (RLS) on all tables
ALTER TABLE app_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_cred ENABLE ROW LEVEL SECURITY;
ALTER TABLE userFriends ENABLE ROW LEVEL SECURITY;
ALTER TABLE groupie ENABLE ROW LEVEL SECURITY;
ALTER TABLE userGroups ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE archiveTasks ENABLE ROW LEVEL SECURITY;

-- Grant permissions to service_role
GRANT ALL ON public.app_user TO service_role;
GRANT ALL ON public.user_cred TO service_role;
GRANT ALL ON public.userFriends TO service_role;
GRANT ALL ON public.groupie TO service_role;
GRANT ALL ON public.userGroups TO service_role;
GRANT ALL ON public.chat TO service_role;
GRANT ALL ON public.calendar TO service_role;
GRANT ALL ON public.tasks TO service_role;
GRANT ALL ON public.archiveTasks TO service_role;

-- Grant permissions to authenticated users
GRANT SELECT, INSERT ON public.app_user TO authenticated;
GRANT SELECT ON public.userFriends TO authenticated;
GRANT SELECT ON public.groupie TO authenticated;
GRANT SELECT ON public.userGroups TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.chat TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.calendar TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.tasks TO authenticated;
GRANT SELECT ON public.archiveTasks TO authenticated;

-- ============================================================================
-- APP_USER - Users can view their own profile, server can manage all
-- ============================================================================

-- Users: SELECT own profile
CREATE POLICY "Users can view own profile"
ON app_user FOR SELECT
USING (UserID = auth.uid());

-- Users: INSERT own profile (for signup)
CREATE POLICY "Users can insert own profile"
ON app_user FOR INSERT
WITH CHECK (UserID = auth.uid() AND auth.role() = 'authenticated');

-- Server: Full access via service_role
CREATE POLICY "Server: manage app_user"
ON app_user FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to clear expired invitation codes (older than 30 minutes)
CREATE OR REPLACE FUNCTION clear_expired_inv_codes()
RETURNS void AS $$
BEGIN
  UPDATE public.groupie
  SET inv_code = NULL
  WHERE inv_code IS NOT NULL
  AND created_at <= now() - interval '30 minutes';
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission to service_role
GRANT EXECUTE ON FUNCTION clear_expired_inv_codes() TO service_role;
GRANT EXECUTE ON FUNCTION clear_expired_inv_codes() TO authenticated;

-- ============================================================================
-- USER_CRED - Server only access
-- ============================================================================

-- Server: INSERT credentials
CREATE POLICY "Server: insert user credentials"
ON user_cred FOR INSERT
WITH CHECK (auth.role() = 'service_role');

-- Server: UPDATE credentials
CREATE POLICY "Server: update user credentials"
ON user_cred FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- Server: SELECT credentials (for authentication)
CREATE POLICY "Server: select user credentials"
ON user_cred FOR SELECT
USING (auth.role() = 'service_role');

-- ============================================================================
-- USERFRIENDS - Users can view their friends list, server manages it
-- ============================================================================

-- Users: SELECT own friendships
CREATE POLICY "Users can view their friends"
ON userFriends FOR SELECT
USING (UserID_1 = auth.uid() OR UserID_2 = auth.uid());

-- Server: Manage friendships
CREATE POLICY "Server: manage friendships"
ON userFriends FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- GROUPIE - Users can view groups they're in, server manages all
-- ============================================================================

-- Users: SELECT only groups they're members of
CREATE POLICY "Users can view groups they joined"
ON groupie FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = groupie.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- Server: Manage groups
CREATE POLICY "Server: manage groups"
ON groupie FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- USERGROUPS - Users can view their group memberships, server manages all
-- ============================================================================

-- Users: SELECT own group memberships
CREATE POLICY "Users can view their group memberships"
ON userGroups FOR SELECT
USING (UserID = auth.uid());

-- Server: Manage group memberships
CREATE POLICY "Server: manage group memberships"
ON userGroups FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- CHAT - Users can view their messages, insert/update their sent messages
-- ============================================================================

-- Users: SELECT messages (sent or received)
CREATE POLICY "Users can view their chat messages"
ON chat FOR SELECT
USING (UserID_sender = auth.uid() OR UserID_receiver = auth.uid());

-- Users: INSERT new messages (as sender)
CREATE POLICY "Users can send chat messages"
ON chat FOR INSERT
WITH CHECK (UserID_sender = auth.uid());

-- Users: UPDATE their sent messages
CREATE POLICY "Users can update their sent messages"
ON chat FOR UPDATE
USING (UserID_sender = auth.uid())
WITH CHECK (UserID_sender = auth.uid());

-- ============================================================================
-- CALENDAR - Users can view/insert/update events in their groups
-- ============================================================================

-- Users: SELECT calendar events for groups they're in
CREATE POLICY "Users can view calendar events in their groups"
ON calendar FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = calendar.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- Users: INSERT calendar events in their groups
CREATE POLICY "Users can create calendar events in their groups"
ON calendar FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = calendar.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- Users: UPDATE calendar events in their groups
CREATE POLICY "Users can update calendar events in their groups"
ON calendar FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = calendar.GroupID
    AND userGroups.UserID = auth.uid()
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = calendar.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- ============================================================================
-- TASKS - Users can view/insert/update tasks in their groups
-- ============================================================================

-- Users: SELECT tasks from their groups
CREATE POLICY "Users can view tasks in their groups"
ON tasks FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = tasks.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- Users: INSERT tasks in their groups
CREATE POLICY "Users can create tasks in their groups"
ON tasks FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = tasks.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- Users: UPDATE tasks in their groups
CREATE POLICY "Users can update tasks in their groups"
ON tasks FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = tasks.GroupID
    AND userGroups.UserID = auth.uid()
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM userGroups
    WHERE userGroups.GroupID = tasks.GroupID
    AND userGroups.UserID = auth.uid()
  )
);

-- ============================================================================
-- ARCHIVETASKS - Users can view archived tasks, server manages all
-- ============================================================================

-- Users: SELECT their archived tasks
CREATE POLICY "Users can view their archived tasks"
ON archiveTasks FOR SELECT
USING (UserID = auth.uid());

-- Server: Manage archived tasks
CREATE POLICY "Server: manage archived tasks"
ON archiveTasks FOR ALL
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

-- ============================================================================
-- STORAGE POLICIES
-- ============================================================================

-- Enable Row Level Security on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Grant permissions to service_role for storage
GRANT ALL ON storage.objects TO service_role;
GRANT ALL ON storage.buckets TO service_role;

-- Grant permissions to authenticated users for storage
GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated;
GRANT SELECT ON storage.buckets TO authenticated;

-- ============================================================================
-- PROFILE_IMAGES BUCKET POLICIES
-- ============================================================================

-- Users can view all profile images (to display in profiles)
CREATE POLICY "Users can view profile images"
ON storage.objects FOR SELECT
USING (bucket_id = 'profile_images');

-- Users can upload profile images (initial upload to temp path)
CREATE POLICY "Users can upload profile images"
ON storage.objects FOR INSERT
WITH CHECK (
  bucket_id = 'profile_images' AND
  auth.role() = 'authenticated'
);

-- Users can update their own profile images (including moves)
CREATE POLICY "Users can update profile images"
ON storage.objects FOR UPDATE
USING (
  bucket_id = 'profile_images' AND
  auth.role() = 'authenticated'
)
WITH CHECK (
  bucket_id = 'profile_images' AND
  auth.role() = 'authenticated' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Users can delete their own profile images
CREATE POLICY "Users can delete own profile images"
ON storage.objects FOR DELETE
USING (
  bucket_id = 'profile_images' AND
  auth.role() = 'authenticated' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Server: Full access to profile_images bucket
CREATE POLICY "Server: manage profile images"
ON storage.objects FOR ALL
USING (
  bucket_id = 'profile_images' AND
  auth.role() = 'service_role'
)
WITH CHECK (
  bucket_id = 'profile_images' AND
  auth.role() = 'service_role'
);
