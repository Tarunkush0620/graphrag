import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { Outlet, RouterProvider, createBrowserRouter, Navigate } from "react-router-dom";
import Benchmark from "./pages/Benchmark.tsx";
import Dashboard from "./pages/Dashboard.tsx";
import Investigate from "./pages/Investigate.tsx";
import Compare from "./pages/Compare.tsx";
import KnowledgeGraph from "./pages/KnowledgeGraph.tsx";
import Documents from "./pages/Documents.tsx";
import Chat from "./pages/Chat";
import ChatDialog from "./pages/ChatDialog.tsx";
import TraceLogs from "./pages/TraceLogs.tsx";
import SetupLayout from "./pages/setup/SetupLayout.tsx";
import KGAdmin from "./pages/setup/KGAdmin.tsx";
import IngestGraph from "./pages/setup/IngestGraph.tsx";
import LLMConfig from "./pages/setup/LLMConfig.tsx";
import GraphDBConfig from "./pages/setup/GraphDBConfig.tsx";
import GraphRAGConfig from "./pages/setup/GraphRAGConfig.tsx";
import McpServersConfig from "./pages/setup/McpServersConfig.tsx";
import CustomizePrompts from "./pages/setup/CustomizePrompts.tsx";
import { ThemeProvider } from "./components/ThemeProvider.tsx";
import { ModeToggle } from "@/components/ModeToggle.tsx";
import { useIdleTimeout } from "./hooks/useIdleTimeout.ts";

import "./components/i18n";

/** Redirect to login if no credentials in session. */
const RequireAuth = ({ children }: { children: any }) => {
  if (!sessionStorage.getItem("auth")) {
    return <Navigate to="/" replace />;
  }
  return children;
};


const Layout = () => {
  useIdleTimeout();
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <ModeToggle />
      <Outlet />
    </ThemeProvider>
  );
};

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        path: "/",
        element: <Dashboard />,
      },
      {
        path: "/dashboard",
        element: <Dashboard />,
      },
      {
        path: "/investigate",
        element: <Investigate />,
      },
      {
        path: "/compare",
        element: <Compare />,
      },
      {
        path: "/benchmark",
        element: <Benchmark />,
      },
      {
        path: "/graph",
        element: <KnowledgeGraph />,
      },
      {
        path: "/documents",
        element: <Documents />,
      },
      {
        path: "/login",
        element: <App />,
      },
      {
        path: "/chat",
        element: <Chat />,
      },
      {
        path: "/chat-dialog",
        element: <RequireAuth><ChatDialog /></RequireAuth>,
      },
      {
        path: "/preferences",
        element: <RequireAuth><ChatDialog /></RequireAuth>,
      },
      {
        path: "/trace/:messageId",
        element: <RequireAuth><TraceLogs /></RequireAuth>,
      },
      {
        path: "/setup",
        element: <RequireAuth><SetupLayout /></RequireAuth>,
        children: [
          {
            path: "",
            element: <Navigate to="/setup/kg-admin" replace />,
          },
          {
            path: "kg-admin",
            element: <KGAdmin />,
          },
          {
            path: "kg-admin/ingest",
            element: <IngestGraph />,
          },
          {
            path: "server-config",
            element: <Navigate to="/setup/server-config/llm" replace />,
          },
          {
            path: "server-config/llm",
            element: <LLMConfig />,
          },
          {
            path: "server-config/graphdb",
            element: <GraphDBConfig />,
          },
          {
            path: "server-config/graphrag",
            element: <GraphRAGConfig />,
          },
          {
            path: "server-config/mcp-servers",
            element: <McpServersConfig />,
          },
          {
            path: "prompts",
            element: <CustomizePrompts />,
          },
        ],
      },
      {
        path: "*",
        element: <Navigate to="/" replace />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <RouterProvider router={router} />,
);
