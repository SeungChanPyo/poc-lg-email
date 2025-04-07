from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
import uuid
import time

class TableRequest(BaseModel):
    file: UploadFile = File(...)