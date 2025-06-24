import RankButton from "./RankButton";

type OptionState = {
  rank: number;
  discarded: boolean;
};

type RankSelectorProps = {
  optionStates: OptionState[];
  currentRank: number; // Current rank of this option (0 means unranked)
  maxRank: number; // Total number of active options (determines button count)
  onRankChange: (rank: number) => void; // Callback when rank changes
};

export default function RankSelector({
  optionStates,
  currentRank,
  maxRank,
  onRankChange,
}: RankSelectorProps) {
  // Generate buttons from 1 to maxRank
  const buttons = Array.from({ length: maxRank }, (_, i) => i + 1);

  // Checks if a rank is already taken by another option
  function isRankTaken(rank: number) {
    return optionStates.some(
      (state) => state.rank === rank && !state.discarded
    );
  }

  // Checks if a button should be disabled
  function isButtonDisabled(rank: number) {
    // If this option is already ranked (but not with this rank) => disable
    if (currentRank > 0 && currentRank !== rank) return true;

    // If this rank is taken by another option => disable
    if (isRankTaken(rank) && currentRank !== rank) return true;

    return false;
  }

  return (
    <div style={{ display: "flex", gap: "0.5rem", flexDirection: "row", justifyContent:"center" }}>
      {buttons.map((rank) => (
        <RankButton
          key={rank}
          rank={rank}
          isSelected={currentRank === rank}
          isDisabled={isButtonDisabled(rank)}
          onClick={() => onRankChange(currentRank === rank ? 0 : rank)}
        />
      ))}
    </div>
  );
}
