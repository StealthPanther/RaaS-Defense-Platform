"""
Recovery and Decryption Tools API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from loguru import logger

router = APIRouter()


class RecoveryToolInfo(BaseModel):
    """Recovery tool information"""
    name: str
    ransomware_family: str
    description: str
    url: str
    supported_extensions: List[str]


# Ransomware decryption tools database
RECOVERY_TOOLS = [
    {
        "name": "No More Ransom - Avast Decryptor",
        "ransomware_family": "WannaCry",
        "description": "Free decryption tool for WannaCry ransomware variants",
        "url": "https://www.nomoreransom.org/en/decryption-tools.html",
        "supported_extensions": [".WNCRY", ".WCRY", ".WNCRYT"]
    },
    {
        "name": "Kaspersky RakhniDecryptor",
        "ransomware_family": "Rakhni/Agent.iih/Aura/Autoit/Pletor/Rotor/Lamer/Lortok/Cryptokluchen/Democry",
        "description": "Multi-purpose decryption tool by Kaspersky",
        "url": "https://support.kaspersky.com/viruses/disinfection/4555",
        "supported_extensions": [".locked", ".kraken", ".darkness", ".nochance"]
    },
    {
        "name": "Emsisoft Decryptor for STOP Djvu",
        "ransomware_family": "STOP Djvu",
        "description": "Decryptor for STOP Djvu ransomware family",
        "url": "https://www.emsisoft.com/ransomware-decryption-tools/stop-djvu",
        "supported_extensions": [".djvu", ".udjvu", ".djvuu", ".djvur"]
    },
    {
        "name": "Trend Micro Ransomware File Decryptor",
        "ransomware_family": "Multiple families",
        "description": "Tool supporting multiple ransomware families",
        "url": "https://success.trendmicro.com/dcx/s/solution/1114221",
        "supported_extensions": [".cerber", ".locky", ".teslacrypt"]
    },
    {
        "name": "Avast Decryptor for AES_NI",
        "ransomware_family": "AES_NI",
        "description": "Free decryption for AES_NI ransomware",
        "url": "https://www.avast.com/ransomware-decryption-tools",
        "supported_extensions": [".aes_ni"]
    },
    {
        "name": "Emsisoft Decryptor for Jigsaw",
        "ransomware_family": "Jigsaw",
        "description": "Decryptor for Jigsaw ransomware",
        "url": "https://www.emsisoft.com/ransomware-decryption-tools/jigsaw",
        "supported_extensions": [".fun", ".kkk", ".btc"]
    }
]


@router.get("/tools", response_model=List[RecoveryToolInfo])
async def get_recovery_tools():
    """
    Get list of available ransomware recovery tools
    
    Returns:
        List of recovery tools with information
    """
    try:
        return RECOVERY_TOOLS
    except Exception as e:
        logger.error(f"Error fetching recovery tools: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recovery tools")


@router.get("/identify/{extension}")
async def identify_ransomware(extension: str):
    """
    Identify ransomware family by file extension
    
    Args:
        extension: File extension (with or without leading dot)
        
    Returns:
        Matching recovery tools and ransomware family info
    """
    try:
        # Normalize extension
        if not extension.startswith('.'):
            extension = f".{extension}"
        extension = extension.lower()
        
        # Find matching tools
        matching_tools = []
        for tool in RECOVERY_TOOLS:
            if extension in [ext.lower() for ext in tool['supported_extensions']]:
                matching_tools.append(tool)
        
        if not matching_tools:
            return {
                "extension": extension,
                "identified": False,
                "message": "No known decryption tools for this extension. Contact cybersecurity professionals.",
                "tools": [],
                "general_advice": [
                    "Do NOT pay the ransom",
                    "Disconnect infected devices from network",
                    "Report to authorities (FBI's IC3, local police)",
                    "Contact professional incident response team",
                    "Check ID Ransomware (id-ransomware.malwarehunterteam.com)",
                    "Try generic recovery tools from No More Ransom project"
                ]
            }
        
        return {
            "extension": extension,
            "identified": True,
            "ransomware_families": list(set([tool['ransomware_family'] for tool in matching_tools])),
            "tools": matching_tools,
            "recovery_steps": [
                "Disconnect infected device from network immediately",
                "Do NOT delete encrypted files or ransom note",
                "Document everything (screenshots, ransom note content)",
                "Download recommended decryption tool(s)",
                "Make backup of encrypted files before attempting decryption",
                "Follow tool-specific instructions carefully",
                "Report incident to authorities"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error identifying ransomware by extension {extension}: {e}")
        raise HTTPException(status_code=500, detail="Identification failed")


@router.get("/search")
async def search_tools(query: str):
    """
    Search recovery tools by ransomware family name or keyword
    
    Args:
        query: Search query
        
    Returns:
        Matching recovery tools
    """
    try:
        query_lower = query.lower()
        matching_tools = []
        
        for tool in RECOVERY_TOOLS:
            if (query_lower in tool['ransomware_family'].lower() or
                query_lower in tool['name'].lower() or
                query_lower in tool['description'].lower()):
                matching_tools.append(tool)
        
        return {
            "query": query,
            "found": len(matching_tools),
            "tools": matching_tools
        }
        
    except Exception as e:
        logger.error(f"Error searching recovery tools: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
