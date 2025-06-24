type RankButtonProps = {
  rank: number; // The rank number this button represents
  isSelected: boolean; // Whether this rank is currently selected
  isDisabled: boolean; // Whether this button should be disabled
  onClick: () => void; // Click handler
};

export default function RankButton({
  rank,
  isSelected,
  isDisabled,
  onClick,
}: RankButtonProps) {
  return (
    <button
      style={{
        all: "unset",
        cursor: isDisabled ? "not-allowed" : "pointer",
        fontFamily: "Victor Mono",
        transition: "all 0.2s ease",
        textDecoration: isSelected ? "underline" : "none",
        opacity: isDisabled ? 0.5 : 1,
        filter: isDisabled ? "blur(1px)" : "none",
        padding: "8px",
        color: isDisabled ? "#666" : "#111",
        fontWeight: isSelected ? "bold" : "normal",
      }}
      onClick={onClick}
      disabled={isDisabled}
    >
      {rank}
    </button>
  );
}
