# Sub-Skill: exec-systems-administrator

* **Description:** Configure and manage MCP servers, Obsidian RAG system, and Hermes Agent configuration with persistence across restarts.

---

# Systems Administrator
Configure and manage MCP servers, Obsidian RAG system, and Hermes Agent configuration with persistence across restarts.

## When to Use
- Setting up new MCP server integrations requiring permanent configuration
- Configuring Hermes Agent for system administration with settings that survive restarts
- Repairing or updating Obsidian RAG system with lasting changes
- Ensuring configurations persist across Hermes Desktop app and system restarts

## Prerequisites
- Hermes Agent installed and running
- Node.js and npm available (for npx-based MCP servers)
- UVX available (for uvx-based MCP servers like git)
- Access to required drives/folders: D:\Alex - KV Obsidian, C:\Users\apviz, E:\CLAUDE
- Administrative privileges for installing global npm packages if needed
- Understanding that Hermes prioritizes profile-specific configurations over global settings

## How to Run
Invoke through the `hermes mcp` command group or directly edit Hermes configuration files, ensuring profile-specific configurations are set for persistence.

## Quick Reference
- `hermes mcp list` - List configured MCP servers
- `hermes mcp test <name>` - Test connection to an MCP server
- `hermes mcp add <name> --command <cmd> --args <args...>` - Add new MCP server
- `hermes mcp remove <name>` - Remove MCP server
- Edit `C:\Users\apviz\AppData\Local\hermes\profiles\<profile>\config.yaml` for persistent profile-specific configuration
- Edit `C:\Users\apviz\AppData\Local\hermes\config.yaml` for global configuration (may be overridden by profile settings)
- Run `python health_check.py` in Obsidian RAG scripts directory to verify RAG system

## Procedure
1. **List current MCP servers**:
   ```
   hermes mcp list
   ```

2. **Add filesystem MCP server** (provides file access):
   ```
   hermes mcp add filesystem --command npx --args -y @modelcontextprotocol/server-filesystem "D:\Alex - KV Obsidian" "C:\Users\apviz" "E:\CLAUDE"
   ```

3. **Add Obsidian MCP server** (provides vault access):
   ```
   hermes mcp add obsidian --command npx --args -y @huangyihe/obsidian-mcp --vault-path "D:\Alex - KV Obsidian\Alex - KV Obsidian"
   ```

4. **Add browser MCP server** (provides web automation):
   ```
   hermes mcp add browser --command npx --args -y @modelcontextprotocol/server-puppeteer
   ```

5. **Add git MCP server** (provides version control):
   ```
   hermes mcp add git --command uvx --args mcp-server-git
   ```

6. **Add memory MCP server** (provides persistent knowledge graph):
   ```
   hermes mcp add memory --command npx --args -y @modelcontextprotocol/server-memory
   ```

7. **Add Qwen MCP server** (provides Qwen CLI integration):
   ```
   hermes mcp add qwen --command npx --args -y @gy920/qwen-mcp-tool
   ```

8. **Add sequential-thinking MCP server** (provides reasoning capabilities):
   ```
   hermes mcp add sequential-thinking --command npx --args -y @modelcontextprotocol/server-sequential-thinking
   ```

9. **Add chrome-devtools MCP server** (provides browser DevTools access):
   ```
   hermes mcp add chrome-devtools --command npx --args -y chrome-devtools-mcp@latest
   ```

10. **Test all servers**:
    ```
    hermes mcp test filesystem
    hermes mcp test obsidian
    hermes mcp test browser
    hermes mcp test git
    hermes mcp test memory
    hermes mcp test qwen
    hermes mcp test sequential-thinking
    hermes mcp test chrome-devtools
    ```

11. **Configure via config.yaml for PERSISTENCE** (critical for settings that survive restarts):
    - For the DEFAULT Orchestrator profile, edit: `C:\Users\apviz\AppData\Local\hermes\profiles\default\config.yaml`
    - For other profiles, edit: `C:\Users\apviz\AppData\Local\hermes\profiles\<profile_name>\config.yaml`
    - Add or modify the `mcp_servers` section with proper command, args, and timeout
    - Example structure:
      ```yaml
      mcp_servers:
        filesystem:
          command: npx
          args:
            - -y
            - '@modelcontextprotocol/server-filesystem'
            - D:\Alex - KV Obsidian
            - C:\Users\apviz
            - E:\CLAUDE
          timeout: 60
      ```
    - Save and restart Hermes for changes to take effect
    - **NOTE**: Profile-specific configurations in `/profiles/<profile>/config.yaml` take precedence over global settings in `/config.yaml`

12. **Repair Obsidian RAG system** (if needed):
    - Update paths in scripts under `C:\Users\apviz\AppData\Local\hermes\skills\note-taking\obsidian-rag\scripts\`
    - Set correct vault path: `D:\Alex - KV Obsidian`
    - Set correct index path: `D:\Alex - KV Obsidian\.vault-intelligence\chroma`
    - Run health check: `python health_check.py` in the scripts directory

## Pitfalls
- **Path splitting issue**: When using npx with paths containing spaces (like "D:\Alex - KV Obsidian"), some MCP servers may split the path incorrectly. Use the SSE bridge solution for Qwen Desktop App or ensure proper quoting.
- **Service conflicts**: Only one service can listen on a specific port. Ensure MCP servers don't conflict with existing services.
- **Node.js version**: Some MCP servers may require specific Node.js versions. Use nvm or similar to manage versions if needed.
- **UVX availability**: UVX-based servers (like git) require UVX to be installed and in PATH.
- **Permission errors**: Running MCP servers that access system folders may require administrative privileges.
- **Configuration precedence**: Hermes prioritizes profile-specific configurations (`/profiles/<profile>/config.yaml`) over global settings (`/config.yaml`). Settings in the global config may be overridden by profile settings on restart.
- **Profile specificity**: To make settings permanent for your Orchestrator instance, you MUST configure the specific profile you're using (default: `default` profile). Global configuration alone may not persist if profile-specific config exists.
- **Skill update status**: When skills**: Skills showing as "update_available" in `hermes skills check` are still installed and functional - they simply have newer versions available. The UI may display them differently, but they remain installed until explicitly updated or removed. To update skills: `hermes skills update <skill_name>` or `hermes skills update` for all available updates.

## Verification
Run `hermes mcp list` and confirm all expected servers appear with status "✓ enabled" and show the correct number of tools discovered. To verify persistence:
1. Close and restart Hermes Desktop app
2. Run `hermes mcp list` again
3. Confirm all previously configured servers remain listed with "✓ enabled" status