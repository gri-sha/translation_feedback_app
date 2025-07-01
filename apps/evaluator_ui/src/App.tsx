import { useState, useMemo, useEffect } from "react";
import TranslationOptions from "./components/TranslationOptions";
import TargetContext from "./components/TargetContext";
import Continue from "./components/Continue";

type OptionState = {
  rank: number;
  discarded: boolean;
};

type TargetContextData = {
  id: number;
  context1: string;
  target: string;
  context2: string;
};

type TranslationData = {
  id: number;
  targetId: number;
  translation: string;
  model: string;
  numEvals: number;
};

type EvaluationData = {
  translationId: number;
  rank: number;
  discarded: boolean;
};

function App() {
  const [targetContextData, setTargetContextData] =
    useState<TargetContextData | null>(null);
  const [translations, setTranslations] = useState<TranslationData[]>([]);
  const [optionStates, setOptionStates] = useState<OptionState[]>([]);

  const fetchData = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/get_target");
      const data = await response.json();
      console.log(data);
      setTargetContextData(data.target);
      setTranslations(data.translations);
      setOptionStates(
        data.translations.map(() => ({ rank: 0, discarded: false }))
      );
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const isComplete = useMemo(() => {
    return !optionStates.some(
      (state) => state.rank === 0 && state.discarded === false
    );
  }, [optionStates]);

  const submitEvaluation = async (): Promise<void> => {
    if (isComplete) {
      const response: EvaluationData[] = [];

      for (let i = 0; i < translations.length; i++) {
        response.push({
          translationId: translations[i].id,
          rank: optionStates[i].rank,
          discarded: optionStates[i].discarded,
        });
      }

      console.log(response)

      try {
        const res = await fetch("http://127.0.0.1:5000/submit_evaluation", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(response),
        });

        if (res.ok) {
          const result = await res.json();
          console.log(result.message);
          fetchData();
        } else {
          const error = await res.json();
          console.error("Error:", error.error);
        }
      } catch (err) {
        console.error("Network error:", err);
      }
    } else {
      console.log("NOT COMPLETE");
    }
  };

  if (
    !targetContextData ||
    translations.length === 0 ||
    optionStates.length === 0
  ) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container">
      <div className="column">
        <TargetContext {...targetContextData} />
      </div>
      <div className="column">
        <TranslationOptions
          options={translations}
          optionStates={optionStates}
          setOptionStates={setOptionStates}
        />
        <Continue isComplete={isComplete} onClick={submitEvaluation} />
      </div>
    </div>
  );
}

export default App;
