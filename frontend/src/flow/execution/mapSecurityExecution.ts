export type ExecutionStep={name:string;state:string;detail:string};
export const stages=['Request','Authentication','Tenant Resolver','Membership','RBAC','DB Tenant Context','Repository Query','PostgreSQL RLS','Feature Gate','Quota','Mutation','Audit','Response'];
export function mapSecurityExecution(label:string,evidence:Record<string,unknown>={}):ExecutionStep[]{
  const denied=label.includes('Viewer')||label.includes('Quota')||label.includes('Cross');
  return stages.map((name,index)=>({name,state:index===0?'succeeded':(denied&&index>=4?'skipped':'succeeded'),detail:index===4&&denied?'Denied / filtered by policy':index===7?`RLS: ${evidence.rows_visible??'tenant-only'} visible rows`:'Backend execution stage'}));
}
