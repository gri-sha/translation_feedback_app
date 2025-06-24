import { useState, useMemo } from "react";
import TranslationOptions from "./components/TranslationOptions";
import TargetContext from "./components/TargetContext";
import Continue from "./components/Continue";

type OptionState = {
  rank: number;
  discarded: boolean;
};

const targetContextData = {
  context1:
    "The first computer program is generally dated to 1843 when mathematician Ada Lovelace published an algorithm to calculate a sequence of Bernoulli numbers, intended to be carried out by Charles Babbage's Analytical Engine. ",
  target:
    "The algorithm, which was conveyed through notes on a translation of Luigi Federico Menabrea's paper on the analytical engine was mainly conceived by Lovelace as can be discerned through her correspondence with Babbage.",
  context2:
    " However, Charles Babbage himself had written a program for the AE in 1837. Lovelace was also the first to see a broader application for the analytical engine beyond mathematical calculations.",
};

const translations = [
  "L'algorithme, qui fut transmis par le biais de notes sur une traduction de l'article de Luigi Federico Menabrea concernant la machine analytique, fut principalement conçu par Lovelace, comme on peut le discerner à travers sa correspondance avec Babbage.",
  "Cet algorithme, communiqué dans des notes accompagnant une traduction du mémoire de Luigi Federico Menabrea sur la machine analytique, fut essentiellement l'œuvre de Lovelace, ainsi qu'en témoigne sa correspondance avec Babbage.",
  "L'algorithme, présenté dans des notes sur une traduction de l'article de Luigi Federico Menabrea relatif à la machine analytique, était principalement le fruit de la conception de Lovelace, comme le révèle sa correspondance avec Babbage.",
  "L'algorithme, exposé à travers des notes sur une traduction du texte de Luigi Federico Menabrea portant sur la machine analytique, fut avant tout conçu par Lovelace elle-même, ce que confirme sa correspondance avec Babbage.",
];

function App() {
  const [optionStates, setOptionStates] = useState<OptionState[]>(
    translations.map(() => ({ rank: 0, discarded: false }))
  );

  const isComplete = useMemo(() => {
    return !optionStates.some(
      (state) => state.rank === 0 && state.discarded === false
    );
  }, [optionStates]);

  const saveSelections = () => {
    if (isComplete) {
      console.log("Selected translations:", optionStates);
    } else {
      console.log("NOT COMPLETE");
    }
  };

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
        <Continue isComplete={isComplete} onClick={saveSelections} />
      </div>
    </div>
  );
}

export default App;
