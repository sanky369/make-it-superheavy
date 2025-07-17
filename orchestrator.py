import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from agent import OpenRouterAgent
from model_factory import ModelFactory, ModelAwareAgent
from config_utils import load_config

class TaskOrchestrator:
    def __init__(self, config_path="config.yaml", silent=False, agent_model=None):
        # Load configuration
        self.config = load_config(config_path)
        
        self.num_agents = self.config['orchestrator']['parallel_agents']
        self.task_timeout = self.config['orchestrator']['task_timeout']
        self.aggregation_strategy = self.config['orchestrator']['aggregation_strategy']
        self.silent = silent
        
        # Initialize model factory
        self.model_factory = ModelFactory(config_path)
        
        # Set orchestrator model (fixed as kimi-k2 per requirements)
        self.orchestrator_model = self.config['models']['orchestrator']['model_key']
        
        # Set agent model (can be overridden, defaults to config)
        if agent_model:
            self.agent_model = agent_model
        else:
            self.agent_model = self.config['models']['default_agent']['model_key']
        
        # Track agent progress
        self.agent_progress = {}
        self.agent_results = {}
        self.progress_lock = threading.Lock()
    
    def decompose_task(self, user_input: str, num_agents: int) -> List[str]:
        """Use AI to dynamically generate different questions based on user input"""
        
        # Create question generation agent using orchestrator model (kimi-k2)
        question_agent = ModelAwareAgent(self.orchestrator_model, silent=True)
        
        # Get question generation prompt from config
        prompt_template = self.config['orchestrator']['question_generation_prompt']
        generation_prompt = prompt_template.format(
            user_input=user_input,
            num_agents=num_agents
        )
        
        # Remove task completion tool to avoid issues
        question_agent.tools = [tool for tool in question_agent.tools if tool.get('function', {}).get('name') != 'mark_task_complete']
        question_agent.tool_mapping = {name: func for name, func in question_agent.tool_mapping.items() if name != 'mark_task_complete'}
        
        try:
            # Get AI-generated questions
            response = question_agent.run(generation_prompt)
            
            # Parse JSON response
            questions = json.loads(response.strip())
            
            # Validate we got the right number of questions
            if len(questions) != num_agents:
                raise ValueError(f"Expected {num_agents} questions, got {len(questions)}")
            
            return questions
            
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: create simple variations if AI fails
            return [
                f"Research comprehensive information about: {user_input}",
                f"Analyze and provide insights about: {user_input}",
                f"Find alternative perspectives on: {user_input}",
                f"Verify and cross-check facts about: {user_input}"
            ][:num_agents]
    
    def update_agent_progress(self, agent_id: int, status: str, result: str = None):
        """Thread-safe progress tracking"""
        with self.progress_lock:
            self.agent_progress[agent_id] = status
            if result is not None:
                self.agent_results[agent_id] = result
    
    def run_agent_parallel(self, agent_id: int, subtask: str) -> Dict[str, Any]:
        """
        Run a single agent with the given subtask.
        Returns result dictionary with agent_id, status, and response.
        """
        try:
            self.update_agent_progress(agent_id, "PROCESSING...")
            
            # Use model-aware agent with configured model
            agent = ModelAwareAgent(self.agent_model, silent=True)
            
            start_time = time.time()
            response = agent.run(subtask)
            execution_time = time.time() - start_time
            
            self.update_agent_progress(agent_id, "COMPLETED", response)
            
            return {
                "agent_id": agent_id,
                "status": "success", 
                "response": response,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Simple error handling
            return {
                "agent_id": agent_id,
                "status": "error",
                "response": f"Error: {str(e)}",
                "execution_time": 0
            }
    
    def aggregate_results(self, agent_results: List[Dict[str, Any]]) -> str:
        """
        Combine results from all agents into a comprehensive final answer.
        Uses the configured aggregation strategy.
        """
        successful_results = [r for r in agent_results if r["status"] == "success"]
        
        if not successful_results:
            return "All agents failed to provide results. Please try again."
        
        # Extract responses for aggregation
        responses = [r["response"] for r in successful_results]
        
        if self.aggregation_strategy == "consensus":
            return self._aggregate_consensus(responses, successful_results)
        else:
            # Default to consensus
            return self._aggregate_consensus(responses, successful_results)
    
    def _aggregate_consensus(self, responses: List[str], _results: List[Dict[str, Any]]) -> str:
        """
        Use one final AI call to synthesize all agent responses into a coherent answer.
        """
        if len(responses) == 1:
            return responses[0]
        
        # Create synthesis agent using dedicated synthesis model (large context window)
        synthesis_config = self.config.get('models', {}).get('synthesis', {})
        synthesis_model = synthesis_config.get('model_key', self.orchestrator_model)
        synthesis_agent = ModelAwareAgent(synthesis_model, silent=True)
        
        # Set max tokens for synthesis if configured
        synthesis_max_tokens = synthesis_config.get('max_tokens', None)
        
        # Build agent responses section
        agent_responses_text = ""
        for i, response in enumerate(responses, 1):
            agent_responses_text += f"=== AGENT {i} RESPONSE ===\n{response}\n\n"
        
        # Get synthesis prompt from config and format it
        synthesis_prompt_template = self.config['orchestrator']['synthesis_prompt']
        synthesis_prompt = synthesis_prompt_template.format(
            num_responses=len(responses),
            agent_responses=agent_responses_text
        )
        
        # Completely remove all tools from synthesis agent to force direct response
        synthesis_agent.tools = []
        synthesis_agent.tool_mapping = {}
        
        # Get the synthesized response with max tokens if configured
        try:
            if synthesis_max_tokens:
                # For synthesis, we need to modify the agent to use max_tokens
                # This is a limitation of the current agent architecture
                # We'll need to call the LLM directly for synthesis
                messages = [
                    {"role": "system", "content": self.config['system_prompt']},
                    {"role": "user", "content": synthesis_prompt}
                ]
                response = synthesis_agent.call_llm(messages, max_tokens=synthesis_max_tokens)
                final_answer = response.choices[0].message.content
            else:
                final_answer = synthesis_agent.run(synthesis_prompt)
            return final_answer
        except Exception as e:
            # Log the error for debugging
            print(f"\n🚨 SYNTHESIS FAILED: {str(e)}")
            print("📋 Falling back to concatenated responses\n")
            # Fallback: if synthesis fails, concatenate responses
            combined = []
            for i, response in enumerate(responses, 1):
                combined.append(f"=== Agent {i} Response ===")
                combined.append(response)
                combined.append("")
            return "\n".join(combined)
    
    def get_progress_status(self) -> Dict[int, str]:
        """Get current progress status for all agents"""
        with self.progress_lock:
            return self.agent_progress.copy()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models for agents"""
        return self.model_factory.get_agent_models()
    
    def get_current_config(self) -> Dict[str, str]:
        """Get current model configuration"""
        synthesis_model = self.config.get('models', {}).get('synthesis', {}).get('model_key', self.orchestrator_model)
        return {
            "orchestrator_model": self.orchestrator_model,
            "synthesis_model": synthesis_model,
            "agent_model": self.agent_model
        }
    
    def set_agent_model(self, model_key: str):
        """Set the model for agents"""
        available_models = self.get_available_models()
        if model_key not in available_models:
            raise ValueError(f"Model {model_key} not available. Available models: {available_models}")
        self.agent_model = model_key
    
    def orchestrate(self, user_input: str):
        """
        Main orchestration method.
        Takes user input, delegates to parallel agents, and returns aggregated result.
        """
        
        # Reset progress tracking
        self.agent_progress = {}
        self.agent_results = {}
        
        # Decompose task into subtasks
        subtasks = self.decompose_task(user_input, self.num_agents)
        
        # Initialize progress tracking
        for i in range(self.num_agents):
            self.agent_progress[i] = "QUEUED"
        
        # Execute agents in parallel
        agent_results = []
        
        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            # Submit all agent tasks
            future_to_agent = {
                executor.submit(self.run_agent_parallel, i, subtasks[i]): i 
                for i in range(self.num_agents)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent, timeout=self.task_timeout):
                try:
                    result = future.result()
                    agent_results.append(result)
                except Exception as e:
                    agent_id = future_to_agent[future]
                    agent_results.append({
                        "agent_id": agent_id,
                        "status": "timeout",
                        "response": f"Agent {agent_id + 1} timed out or failed: {str(e)}",
                        "execution_time": self.task_timeout
                    })
        
        # Sort results by agent_id for consistent output
        agent_results.sort(key=lambda x: x["agent_id"])
        
        # Aggregate results
        final_result = self.aggregate_results(agent_results)
        
        # Auto-save to markdown file if enabled
        if self.config.get('output', {}).get('auto_save', False):
            self._save_output_to_file(user_input, final_result)
        
        return final_result
    
    def _save_output_to_file(self, query, result):
        """Save output to markdown file"""
        try:
            from tools.write_output_tool import WriteOutputTool
            
            # Create write tool
            write_tool = WriteOutputTool(self.config)
            
            # Save output
            save_result = write_tool.execute(query, result)
            
            if save_result.get('success') and not self.silent:
                print(f"💾 Output saved to: {save_result['filepath']}")
            elif not save_result.get('success') and not self.silent:
                print(f"⚠️  Failed to save output: {save_result.get('error')}")
                
        except Exception as e:
            if not self.silent:
                print(f"⚠️  Error saving output: {str(e)}")