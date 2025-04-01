from google import genai
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostProcess:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
    
    def select_top_tools(self, tools, max_tools=10):
        """Select the top tools to tweet about based on upvotes and relevance"""
        if not tools:
            return []
            
        # Create a prompt for Gemini to analyze and select top tools
        prompt = f"""
        I have scraped {len(tools)} tools from Product Hunt. Please analyze these tools and select the top {max_tools} most interesting ones to tweet about.
        Consider factors like upvotes, comments, description quality, and potential impact.
        
        Here are the tools:
        
        {self._format_tools_for_prompt(tools)}
        
        Return only the indices of the top {max_tools} tools in order of priority (0-indexed), separated by commas.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=prompt
            )
            
            if response and response.text:
                # Parse the indices from the response
                indices_text = response.text.strip()
                # Extract numbers from the response
                import re
                indices = [int(idx) for idx in re.findall(r'\d+', indices_text)][:max_tools]
                
                # Return the selected tools
                selected_tools = [tools[idx] for idx in indices if idx < len(tools)]
                logger.info(f"Selected {len(selected_tools)} top tools")
                return selected_tools
            
            # Fallback: sort by upvotes and return top tools
            return sorted(tools, key=lambda x: int(x.get('upvotes', '0')), reverse=True)[:max_tools]
            
        except Exception as e:
            logger.error(f"Error selecting top tools: {str(e)}")
            # Fallback: sort by upvotes and return top tools
            return sorted(tools, key=lambda x: int(x.get('upvotes', '0')), reverse=True)[:max_tools]
    
    def generate_tweet(self, tool):
        """Generate a tweet for a specific tool with hashtags, under 240 characters"""
        prompt = f"""
        Generate a compelling tweet (maximum 240 characters including hashtags and link) about this Product Hunt tool:
        
        Tool Name: {tool.get('tool_name', '')}
        Description: {tool.get('short_description', '')}
        Categories: {', '.join(tool.get('categories', []))}
        Upvotes: {tool.get('upvotes', '0')}
        Link: {tool.get('tool_link', '')}
        
        The tweet should:
        1. Be engaging and informative
        2. Include the tool link at the end
        3. Include 2-3 relevant hashtags based on the tool's categories or functionality
        4. Total length must be under 240 characters (including hashtags and link)
        
        Format: [Engaging text about the tool] [2-3 hashtags] [Link]
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            
            if response and response.text:
                tweet_text = response.text.strip()
                
                # Verify tweet length is under 240 characters
                if len(tweet_text) > 240:
                    # Try to trim the tweet while preserving link and hashtags
                    parts = tweet_text.split(' ')
                    link_part = parts[-1] if 'http' in parts[-1] else ''
                    
                    # Find hashtags (they start with #)
                    hashtag_indices = [i for i, part in enumerate(parts) if part.startswith('#')]
                    hashtags = ' '.join([parts[i] for i in hashtag_indices if i < len(parts)])
                    
                    # Calculate how many characters we need to remove
                    excess = len(tweet_text) - 240
                    
                    # Reconstruct tweet without hashtags and link first
                    content_parts = [part for i, part in enumerate(parts) 
                                    if not part.startswith('#') and 'http' not in part]
                    
                    # Trim content to fit
                    content = ' '.join(content_parts)
                    if excess > 0:
                        content = content[:-(excess+3)] + '...'
                    
                    # Reassemble tweet with hashtags and link
                    tweet_text = f"{content} {hashtags} {link_part}".strip()
                
                logger.info(f"Generated tweet for {tool.get('tool_name')}")
                return tweet_text
            return None
        except Exception as e:
            logger.error(f"Error generating tweet: {str(e)}")
            return None

    
    def _format_tools_for_prompt(self, tools):
        """Format the tools data for the Gemini prompt"""
        formatted_text = ""
        for i, tool in enumerate(tools):
            formatted_text += f"Tool {i}:\n"
            formatted_text += f"Name: {tool.get('tool_name', '')}\n"
            formatted_text += f"Description: {tool.get('short_description', '')}\n"
            formatted_text += f"Categories: {', '.join(tool.get('categories', []))}\n"
            formatted_text += f"Upvotes: {tool.get('upvotes', '0')}\n"
            formatted_text += f"Comments: {tool.get('comments', '0')}\n"
            formatted_text += f"Link: {tool.get('tool_link', '')}\n\n"
        return formatted_text
