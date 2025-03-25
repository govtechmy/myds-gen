"use client"
import { useState } from "react";
import { Button } from "@govtechmy/myds-react/button";
import { TextArea } from "@govtechmy/myds-react/textarea";
import { ThemeSwitch } from "@govtechmy/myds-react/theme-switch";
import { ThemeProvider } from "@govtechmy/myds-react/hooks";
import { Spinner } from "@govtechmy/myds-react/spinner";
import { Callout, CalloutTitle, CalloutContent } from "@govtechmy/myds-react/callout";

import dotenv from 'dotenv';
import Sandpackeditor from "./components/LiveEditor"

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
  const headers_api: any = process.env.MYDS_GEN_API

  const handleRun = async () => {
    setLoading(true);
    try {
      // Simulate sequential API calls
      setStatus("Validating");
      const response1 = await fetch(`/api/py/validate-new-prompt?prompt=${input}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // "X-API-KEY": headers_api
        }
      });
      const data1 = await response1.json();
      // console.log(data1)
      if (data1.valid) {
        setStatus("Learning about the prompt");
        const response2 = await fetch(`/api/py/task_planning?prompt=${input}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // "X-API-KEY": headers_api
          },
        });
        const data2 = await response2.json();

        setStatus("Designing the Layout");
        const wireframeRes = await fetch(`/api/py/wireframe_gen`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // "X-API-KEY": headers_api
          },
          body: JSON.stringify(data2)
        }).then(res => res.json());

        setStatus("Gathering knowledge");
        const contextRes = await fetch(`/api/py/assemble_context`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // "X-API-KEY": headers_api
          },
          body: JSON.stringify({ task: data2, wireframe: wireframeRes })
        }).then(res => res.json());

        setStatus("Generating the code");
        const generationRes = await fetch(`/api/py/generate_component`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // "X-API-KEY": headers_api
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
          // "X-API-KEY": headers_api
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
            // "X-API-KEY": headers_api
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
          // "X-API-KEY": headers_api
        },
        body: JSON.stringify(context_update_body)
      }).then(res => res.json());

      setStatus("Updating code");
      let component_update_body = { task: updatetaskObject, context: updatedContext, tsx: context_update_body.wireframe }
      const update_component_response = await fetch(`/api/py/generate_component_iterate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // "X-API-KEY": headers_api
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
        <div className="flex items-center pt-4 mt-8 px-6 mb-0">
          <h1 className="text-txt-black-900 text-3xl mt-auto px-6">MYDS GEN</h1>
          <div className="ml-auto mt-auto px-6">
          <ThemeSwitch />
          </div>
        </div>
        <div className="p-4 flex gap-10">
          <div className="flex-[1] space-y-4 rounded-lg shadow-card px-6 py-6 ">
            <Callout className="p-2 mb-4" variant="warning" dismissible>
              <CalloutTitle>Known Issue</CalloutTitle>
              <CalloutContent>
                Theme Switcher is not working as intended in the sandbox. Please click on the <a className="font-mono bg-bg-white px-1.5 border">Open Sandbox</a> button to get the most accurate rendering
              </CalloutContent>
            </Callout>
            <div className={`border rounded-md px-6 py-6 ${completed ? 'bg-bg-white-disabled' : 'bg-bg-white'}`} >
              <h2 className={`flex ${completed ? 'text-txt-black-disabled' : 'text-txt-black-900'}  text-xl mb-4`}>
                Describe a component
              </h2>
              <TextArea
                className="h-50  min-h-[50px] mb-4"
                size="small"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Describe your desired component..."
                disabled={completed}
              />
              <Button className="ml-auto" onClick={handleRun} disabled={loading || completed || !input}>
                {loading ?
                  <><span>Processing...</span><Spinner color={"white"} /></> : "Submit"}
              </Button>
            </div>
            {loading && (
              <Callout className="p-2">
                <CalloutTitle>{status}</CalloutTitle>
              </Callout>
            )}
            {completed && (
              <>
              <div className="w-[1px] bg-bg-black-400 h-10 mx-auto"></div>
              <div className="border rounded-md px-6 py-6" >
                <h2 className="flex text-txt-black-900 text-xl mb-4">
                  Describe an update or modification
                </h2>
                <TextArea
                  className="h-50  min-h-[50px] mb-4"
                  size="small"
                  value={newInput}
                  onChange={(e) => setNewInput(e.target.value)}
                  placeholder="Enter an update for the component..."
                />
                <Button className="ml-auto" onClick={handleRunIter} disabled={loading_iter || !newInput}>
                  {loading_iter ?
                    <><span>Processing...</span><Spinner color={"white"} /></> : "Submit"}
                </Button>
                {loading_iter && (
                  <Callout className="p-2">
                    <CalloutTitle>{status}</CalloutTitle>
                  </Callout>
                )}
              </div>
              </>
            )}
          </div>
          <div className="flex-[3] rounded-lg shadow-card ">
            <Sandpackeditor code={code} />
          </div>
        </div>

      </ThemeProvider>
    </main>
  );
}
