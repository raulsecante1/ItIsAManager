import mcp_server.server as msvr

if __name__ == "__main__":

    mcp = msvr.init_mcp()
    mcp.run(transport="http")
    