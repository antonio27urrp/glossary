import ForceGraph2D from "react-force-graph-2d";
import { useEffect, useState } from "react";
import { fetchTerms } from "./api";

// Описываем структуру узла и связи для TypeScript
interface GraphNode {
  id: string;
  name: string;
}

interface GraphLink {
  source: string;
  target: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export default function App() {
  const [data, setData] = useState<GraphData>({ nodes: [], links: [] });

  useEffect(() => {
    fetchTerms().then((terms: any[]) => {
      const nodes: GraphNode[] = terms.map((t) => ({
        id: t.keyword,
        name: t.keyword,
      }));

      const links: GraphLink[] = terms.map((t) => ({
        source: "Glossary",
        target: t.keyword,
      }));

      setData({
        nodes: [{ id: "Glossary", name: "Глоссарий ВКР" }, ...nodes],
        links: links,
      });
    });
  }, []);

  return (
    <div
      style={{ width: "100vw", height: "100vh", backgroundColor: "#1a1a1a" }}
    >
      <ForceGraph2D graphData={data} nodeAutoColorBy="id" nodeLabel="name" />
    </div>
  );
}
