import styles from "../styles/TranslationOptions.module.css";
import RankSelector from "./RankSelector";

type OptionState = {
  rank: number;
  discarded: boolean;
};

type TranslationOptionsProps = {
  options: string[];
  optionStates: OptionState[];
  setOptionStates: (states: React.SetStateAction<OptionState[]>) => void;
};

export default function TranslationOptions({
  options,
  optionStates,
  setOptionStates,
}: TranslationOptionsProps) {
  // Update the rank of a specific option
  const updateRank = (index: number, rank: number) => {
    setOptionStates((prev) => {
      const newStates = [...prev];
      newStates[index] = { ...newStates[index], rank };
      return newStates;
    });
  };

  // Toggle discard status of an option
  const toggleDiscard = (index: number) => {
    setOptionStates((prev) => {
      const newStates = [...prev];
      const currentOption = { ...newStates[index] };
      const wasDiscarded = currentOption.discarded;

      // Toggle discard status and reset rank
      newStates[index] = {
        discarded: !wasDiscarded,
        rank: 0,
      };

      if (!wasDiscarded) {
        if (currentOption.rank > 0) {
          for (let i = 0; i < newStates.length; i++) {
            if (i === index) continue;

            if (newStates[i].rank > currentOption.rank) {
              newStates[i] = {
                ...newStates[i],
                rank: newStates[i].rank - 1,
              };
            }
          }
        } else if (currentOption.rank === 0) {
          for (let i = 0; i < newStates.length; i++) {
            if (i === index) continue;
            if (newStates[i].rank > activeOptions - 1) {
              newStates[i] = {
                discarded: false,
                rank: 0,
              };
            }
          }
        }
      }
      return newStates;
    });
  };

  // Reset all ranks (and discard statuses)
  const resetAllRanks = () => {
    setOptionStates((prev) => {
      return prev.map(() => ({
        discarded: false,
        rank: 0,
      }));
    });
  };

  // Get the current active options (not discarded)
  const activeOptions = optionStates.filter((state) => !state.discarded).length;

  return (
    <>
      <h1 className={styles.translationHeader}>Translations :</h1>
      <table className={styles.table}>
        <thead className={styles.thead}>
          <tr className={styles.tr}>
            <td className={`${styles.td} ${styles.option}`}>
              <h2>Translations</h2>
            </td>
            <td className={`${styles.td} ${styles.rank}`}>
              <h2>Rank</h2>
            </td>
            <td className={`${styles.td} ${styles.discard}`}>
              <h2>Discard</h2>
            </td>
          </tr>
        </thead>
        <tbody>
          {options.map((option, index) => (
            <tr key={index} className={styles.tr}>
              <td className={`${styles.td} ${styles.option}`}>{option}</td>
              <td className={`${styles.td} ${styles.rank}`}>
                {optionStates[index].discarded ? (
                  <span className={`${styles.indicator}`}>Discarded</span>
                ) : (
                  <>
                    <div className={`${styles.naming}`}>Rank :</div>
                    <RankSelector
                      optionStates={optionStates}
                      currentRank={optionStates[index].rank}
                      maxRank={activeOptions}
                      onRankChange={(rank) => updateRank(index, rank)}
                    />
                  </>
                )}
              </td>
              <td className={`${styles.td} ${styles.discard}`}>
                <div className={`${styles.naming}`}>Discard :</div>
                <input
                  type="checkbox"
                  className={styles.checkbox}
                  checked={optionStates[index].discarded}
                  onChange={() => toggleDiscard(index)}
                />
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={3} className={styles.td}>
              <button className={styles.resetButton} onClick={resetAllRanks}>
                Reset All
              </button>
            </td>
          </tr>
        </tfoot>
      </table>
    </>
  );
}
