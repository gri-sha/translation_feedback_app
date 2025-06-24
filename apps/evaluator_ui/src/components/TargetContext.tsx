interface ContextTargetProps {
  context1: string;
  target: string;
  context2: string;
}

export default function TargetContext({
  context1,
  target,
  context2,
}: ContextTargetProps) {
  return (
    <>
      <h1 style={{marginBottom: "8px"}}>Target :</h1>
      <div>
        <span>{context1}</span>
        <span style={{background:"yellow"}}>{target}</span>
        <span>{context2}</span>
      </div>
    </>
  );
}
