"use client"
import { useState } from "react";
import { Button } from "@govtechmy/myds-react/button";
import { TextArea } from "@govtechmy/myds-react/textarea";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import { Spinner } from "@govtechmy/myds-react/spinner";
import { Callout, CalloutTitle, CalloutContent } from "@govtechmy/myds-react/callout";
import { Tag } from "@govtechmy/myds-react/tag";
import dotenv from 'dotenv';
import Sandpackeditor from "./components/LiveEditor"
import Link from "next/link"

dotenv.config()
export default function App() {
  const [input, setInput] = useState("");
  const [code, setCode] = useState(`import { Button } from "@govtechmy/myds-react/button";
import { Callout, CalloutAction, CalloutTitle, CalloutContent } from "@govtechmy/myds-react/callout";
import { Link } from "@govtechmy/myds-react/link";

export default function App() {
  return (
    <Callout>
      <CalloutTitle>Your component will be rendered here</CalloutTitle>
      <CalloutContent>
        Built with the Malaysia Government Design System (MYDS)
      </CalloutContent>
      <CalloutAction>
        
        <Link href="https://design.digital.gov.my" primary underline="None" newTab>
          <Button variant="default-outline">
            {/* The link's destination should be indicated here. */}
            Learn More
          </Button>
        </Link>

      </CalloutAction>
    </Callout>
  );
};`);
  const [loading, setLoading] = useState(false);
  const [loading_iter, setLoading_iter] = useState(false);
  const [status, setStatus] = useState("");
  const [data, setData] = useState({})
  const [completed, setCompleted] = useState(false);
  const [newInput, setNewInput] = useState("");

  const handleRun = async () => {
    setLoading(true);
    try {
      setStatus("Validating");
      const response1 = await fetch(`/api/py/validate-new-prompt?prompt=${input}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });
      const data1 = await response1.json();

      if (data1.valid) {
        setStatus("Learning about the prompt");
        const response2 = await fetch(`/api/py/task_planning?prompt=${input}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const data2 = await response2.json();

        setStatus("Designing the Layout");
        const wireframeRes = await fetch(`/api/py/wireframe_gen`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data2)
        }).then(res => res.json());

        setStatus("Gathering knowledge");
        const contextRes = await fetch(`/api/py/assemble_context`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ task: data2, wireframe: wireframeRes })
        }).then(res => res.json());

        setStatus("Generating the code");
        const generationRes = await fetch(`/api/py/generate_component`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ task: data2, context: contextRes })
        }).then(res => res.json());
        setCode(generationRes.replace(/```tsx\n|\n```/g, ""))
        setData({ task: data2, wireframe: wireframeRes, tsx: generationRes.replace(/"/g, '\\"') })
        setStatus("Completed")
        setCompleted(true);
      }
    } catch (error) {

    }
    setLoading(false);
  };

  const handleRunIter = async () => {
    setLoading_iter(true);
    try {
      let updatedPrompt: any = data
      updatedPrompt["update_prompt"] = newInput
      console.log(updatedPrompt)
      setStatus("Learning about the update");
      const update_task_response = await fetch(`/api/py/task_planning_iter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedPrompt)
      });
      const updatetaskObject = await update_task_response.json();

      let context_update_body
      if (updatetaskObject.update.wireframe) {
        setStatus("Updating the Layout");
        let wireframe_update_body: { [key: string]: any } = { task: updatetaskObject, wireframe: updatedPrompt.wireframe }

        const updatedWireframe = await fetch(`/api/py/wireframe_iter`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(wireframe_update_body)
        }).then(res => res.json());

        context_update_body = { task: updatetaskObject, wireframe: updatedWireframe }
      }
      else {
        context_update_body = { task: updatetaskObject, wireframe: updatedPrompt.wireframe }
      }


      setStatus("Gathering knowledge");
      const updatedContext = await fetch(`/api/py/assemble_context_iter`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(context_update_body)
      }).then(res => res.json());

      setStatus("Updating code");
      let component_update_body = { task: updatetaskObject, context: updatedContext, tsx: context_update_body.wireframe }
      const update_component_response = await fetch(`/api/py/generate_component_iterate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(component_update_body)
      }).then(res => res.json());
      setCode(update_component_response.replace(/```tsx\n|\n```/g, ""))
      setData({ task: updatetaskObject, wireframe: context_update_body.wireframe, tsx: update_component_response.replace(/"/g, '\\"') })
      setStatus("Completed")
    }
    catch (error) {

    }
    setLoading_iter(false);
  };

  return (
    <main className="bg-bg-white">
      <ThemeProvider>
        <div className="mx-auto px-4 sm:px-6 lg:px-8 xl:px-10 2xl:px-12">
          <div className="flex flex-wrap items-center pt-4 mt-8 mb-0 mx-4 md:mx-0">
            <div className="flex-col">
            <h1 className="text-txt-black-900 text-3xl mt-auto sm:px-6 xl:px-8 2xl:px-10 font-bold tracking-tight">MYDS Gen</h1>
            <p className="text-txt-black-900 text-sm mt-auto font-bold tracking-tight sm:px-6 xl:px-8 2xl:px-10 hidden sm:block">Generative UI using the <Link href="https://design.digital.gov.my/" className="underline">MYDS</Link> library</p>
            </div>
            <div className="ml-auto mt-auto sm:px-6 xl:px-8 2xl:px-10">
              <ThemeSwitch as="select" />
            </div>
          </div>
          <div className="p-4 flex flex-col lg:flex-row gap-6 xl:gap-8 2xl:gap-10">
            <div className="lg:flex-[1] space-y-4 rounded-lg shadow-card p-6 w-full lg:w-auto xl:w-1/3 2xl:w-1/4">
              <Tag size="small" dot={true} variant="danger">dev Build</Tag>
              <Callout className="p-2 mb-4" variant="warning" dismissible>
                <CalloutTitle>Known Issue</CalloutTitle>
                <CalloutContent>
                  Themes might not be working as intended in the sandbox. Please click on the <span className="font-mono bg-bg-white px-1.5 border">Open Sandbox</span> button to get the most accurate rendering.
                </CalloutContent>
              </Callout>
              <Callout className="p-2 mb-4" variant="warning" dismissible>
                <CalloutTitle>Known Issue</CalloutTitle>
                <CalloutContent>
                  Sandbox crashes when generated code is too long.
                </CalloutContent>
              </Callout>
              <div className={`border rounded-md p-6 ${completed ? 'bg-bg-white-disabled' : 'bg-bg-white'}`}>
                <h2 className={`flex ${completed ? 'text-txt-black-disabled' : 'text-txt-black-900'} text-xl mb-4 justify-center`}>
                  Describe a component
                </h2>
                <TextArea
                  className="h-50 min-h-[50px] mb-4 w-full"
                  size="small"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe your desired component..."
                  disabled={completed}
                />
                <Button className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto" onClick={handleRun} disabled={loading || completed || !input}>
                  {loading ? <><span>Processing...</span><Spinner color="white" /></> : "Submit"}
                </Button>
              </div>
              {loading && (
                <Callout className="p-2">
                  <CalloutTitle>
                    {status}
                    <span className="inline-block animate-bounce 500ms">.</span>
                    <span className="inline-block animate-bounce 500ms [animation-delay:200ms]">.</span>
                    <span className="inline-block animate-bounce 500ms [animation-delay:400ms]">.</span>
                  </CalloutTitle>
                </Callout>
              )}
              {completed && (
                <>
                  <div className="w-[1px] bg-bg-black-400 h-10 mx-auto"></div>
                  <div className="border rounded-md p-6">
                    <h2 className="flex text-txt-black-900 text-xl mb-4 justify-center">
                      Describe an update or modification
                    </h2>
                    <TextArea
                      className="h-50 min-h-[50px] mb-4 w-full"
                      size="small"
                      value={newInput}
                      onChange={(e) => setNewInput(e.target.value)}
                      placeholder="Enter an update for the component..."
                    />
                    <Button className="ml-auto w-full sm:w-auto xl:w-auto 2xl:w-auto" onClick={handleRunIter} disabled={loading_iter || !newInput}>
                      {loading_iter ? <><span>Processing...</span><Spinner color="white" /></> : "Submit"}
                    </Button>
                  </div>
                  {loading_iter && (
                    <Callout className="p-2">
                      <CalloutTitle>
                        {status}<span> </span>
                        <span className="inline-block animate-bounce 500ms">.</span>
                        <span className="inline-block animate-bounce 500ms [animation-delay:200ms]">.</span>
                        <span className="inline-block animate-bounce 500ms [animation-delay:400ms]">.</span>
                      </CalloutTitle>
                    </Callout>
                  )}
                </>
              )}
            </div>
            <div className="lg:flex-[3] rounded-lg shadow-card w-full xl:w-2/3 2xl:w-3/4">
              <Sandpackeditor code={code} />
            </div>
          </div>
        </div>
      </ThemeProvider>
    </main>
  );
}
