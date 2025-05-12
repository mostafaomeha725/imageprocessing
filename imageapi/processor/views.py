from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .image_processor import process_image
import base64
import numpy as np
import cv2

@api_view(['POST'])
def process_image_api(request):
    try:
        # Get image and parameters from request
        image_file = request.FILES['image']
        method = request.data.get('method', 'Canny')
        low = int(request.data.get('low', 100))
        high = int(request.data.get('high', 200))
        
        # Read image file
        image_bytes = image_file.read()
        
        # Process image (using your existing code)
        processed_img = process_image(image_bytes, method, low, high)
        
        # Convert back to bytes
        _, img_encoded = cv2.imencode('.png', processed_img)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        
        return Response({
            'processed_image': img_base64,
            'method': method
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)