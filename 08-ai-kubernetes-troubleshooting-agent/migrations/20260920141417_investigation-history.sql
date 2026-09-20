CREATE TABLE public.investigations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL DEFAULT auth.uid() REFERENCES auth.users(id) ON DELETE CASCADE,
  cluster_context text NOT NULL,
  status text NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'healthy', 'partial_success', 'error')),
  stage text NOT NULL DEFAULT 'starting',
  root_cause text,
  namespace text,
  confidence smallint CHECK (confidence BETWEEN 0 AND 100),
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX investigations_user_created_idx
  ON public.investigations (user_id, created_at DESC);

ALTER TABLE public.investigations ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.investigations FROM anon, authenticated;
GRANT SELECT, INSERT ON public.investigations TO authenticated;
GRANT UPDATE (status, stage, root_cause, namespace, confidence, error_message)
  ON public.investigations TO authenticated;

CREATE POLICY investigations_select_own ON public.investigations
  FOR SELECT TO authenticated USING (user_id = (SELECT auth.uid()));
CREATE POLICY investigations_insert_own ON public.investigations
  FOR INSERT TO authenticated WITH CHECK (user_id = (SELECT auth.uid()));
CREATE POLICY investigations_update_own ON public.investigations
  FOR UPDATE TO authenticated
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));

CREATE TRIGGER investigations_updated_at
  BEFORE UPDATE ON public.investigations
  FOR EACH ROW EXECUTE FUNCTION system.update_updated_at();

INSERT INTO realtime.channels (pattern, description, enabled)
VALUES ('investigations:%', 'Private investigation progress per user', true)
ON CONFLICT (pattern) DO UPDATE
SET description = EXCLUDED.description, enabled = EXCLUDED.enabled;

ALTER TABLE realtime.channels ENABLE ROW LEVEL SECURITY;
CREATE POLICY investigations_subscribe_own ON realtime.channels
  FOR SELECT TO authenticated
  USING (
    pattern = 'investigations:%'
    AND split_part(realtime.channel_name(), ':', 2) = (SELECT auth.uid())::text
  );

CREATE OR REPLACE FUNCTION public.publish_investigation_progress()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public, pg_temp
AS $$
BEGIN
  PERFORM realtime.publish(
    'investigations:' || NEW.user_id::text,
    'investigation_progress',
    jsonb_build_object(
      'id', NEW.id,
      'status', NEW.status,
      'stage', NEW.stage,
      'root_cause', NEW.root_cause,
      'confidence', NEW.confidence
    )
  );
  RETURN NEW;
END;
$$;

CREATE TRIGGER investigations_publish_progress
  AFTER INSERT OR UPDATE OF status, stage, root_cause, confidence
  ON public.investigations
  FOR EACH ROW EXECUTE FUNCTION public.publish_investigation_progress();
