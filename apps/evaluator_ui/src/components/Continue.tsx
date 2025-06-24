type ContinueProps = {
  isComplete: boolean;
  onClick : () => void;
};

export default function Continue({ isComplete, onClick }: ContinueProps) {
  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        justifyContent: "center",
        marginTop: "32px",
        marginBottom: "64px",
      }}
    >
      <button
        style={{
          all: "unset",
          cursor: "pointer",
          fontFamily: "Victor Mono",
          textDecoration: "underline",
          fontSize: "1.62rem",
          fontWeight: isComplete ? "bolder" : "normal",
          transition: "font-weight 0.3s ease",
        }}
        onClick={onClick}
      >
        Continue
      </button>
    </div>
  );
}
