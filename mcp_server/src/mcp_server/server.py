#from mcp.server import MCPServer
from fastmcp import FastMCP

import pathlib

from starlette.responses import FileResponse

import mcp_server.tools.io_tools as mtit
import mcp_server.config as mcfg


def init_mcp():

    mcp = FastMCP("itIsAMcpServer")
    #mcp.add_tool(mtit.write_article)  # since this dose not make any sense
    mcp.add_tool(mtit.list_readable_files)
    mcp.add_tool(mtit.read_file)

    ''' since we canceled the write file tool
    # the download link
    @mcp.custom_route("/files/{filename}", methods=["GET"])
    async def download_file(filename: str):
        """
        define the download link
        """

        safe_name = pathlib.Path(filename).name
        file_path = mcfg.OUTPUT_DIR / safe_name
        
        if not file_path.exists():
            return {"error": f"file dose not exist: {filename}"}, 404
        
        if file_path.suffix not in {".md", ".txt", ".json", ".pdf"}:
            return {"error": f"unsupported file type: {file_path.suffix}"}, 403
        
        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="text/markdown" if file_path.suffix == ".md" else "text/plain"
        )
    '''

    print("Registered routes:", mcp._routes if hasattr(mcp, '_routes') else "No _routes")
    return mcp
