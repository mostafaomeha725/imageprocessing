import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const ImageProcessingApp());
}

class ImageProcessingApp extends StatelessWidget {
  const ImageProcessingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: const ImageProcessingPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ImageProcessingPage extends StatefulWidget {
  const ImageProcessingPage({super.key});

  @override
  State<ImageProcessingPage> createState() => _ImageProcessingPageState();
}

class _ImageProcessingPageState extends State<ImageProcessingPage> {
  File? _image;
  Uint8List? _processedImageBytes;
  final picker = ImagePicker();
  final TextEditingController methodController = TextEditingController();
  final TextEditingController lowController = TextEditingController();
  final TextEditingController highController = TextEditingController();

  String selectedMethod = '';

  Future<void> _pickImage() async {
    // Request permission to access the gallery

    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _processedImageBytes = null;
      });

      //  _showMessage('Permission denied. Please grant gallery access.');
    }
  }

  Future<void> _uploadImage() async {
    if (_image == null) {
      _showMessage('No image selected');
      return;
    }

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://192.168.1.106:8000/api/process-image/'),
      );

      request.files.add(
        await http.MultipartFile.fromPath('image', _image!.path),
      );

      request.fields.addAll({
        'method': selectedMethod,
        'low':
            lowController.text.isEmpty
                ? '50'
                : lowController.text, // Default to 50 if empty
        'high':
            highController.text.isEmpty
                ? '100'
                : highController.text, // Default to 100 if empty
      });

      //  print('Sending request to server...');
      var response = await request.send();

      //  print('Response status: ${response.statusCode}');
      final respStr = await response.stream.bytesToString();
      //  print('Response body: $respStr');

      if (response.statusCode == 200) {
        final decoded = jsonDecode(respStr);
        if (decoded.containsKey('processed_image')) {
          setState(() {
            _processedImageBytes = base64Decode(decoded['processed_image']);
          });
          _showMessage('Image processed successfully!');
        } else {
          _showMessage('No processed image returned.');
        }
      } else {
        _showMessage('Somthing went wrong');
      }
    } catch (e) {
      _showMessage('Error occurred: $e');
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        centerTitle: true,
        title: const Text(
          "Image Processing",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 24),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 84),
              child: ElevatedButton(
                style: ButtonStyle(
                  backgroundColor: WidgetStateProperty.all(Color(0xff1751ab)),
                ),
                onPressed: _pickImage,
                child: const Text(
                  "Pick Image",
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),
            if (_image != null) ...[
              Center(
                child: const Text(
                  "Original Image",
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 28),
                ),
              ),
              SizedBox(height: 10),
              Image.file(_image!, height: 150),
              const SizedBox(height: 10),
              DropdownButtonFormField<String>(
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please select a method';
                  }
                  return null;
                },
                value: selectedMethod.isEmpty ? null : selectedMethod,
                items: const [
                  DropdownMenuItem(value: 'canny', child: Text('Canny')),
                  DropdownMenuItem(value: 'Sobel', child: Text('Sobel')),
                  DropdownMenuItem(
                    value: 'equalization',
                    child: Text('Equalization'),
                  ),
                  DropdownMenuItem(
                    value: 'laplacian',
                    child: Text('Laplacian'),
                  ),
                  DropdownMenuItem(value: 'prewitt', child: Text('Prewitt')),
                  DropdownMenuItem(value: 'roberts', child: Text('Roberts')),
                ],
                onChanged: (value) {
                  setState(() {
                    selectedMethod = value!;
                    // Reset low and high when method changes
                    lowController.clear();
                    highController.clear();
                  });
                },
                decoration: const InputDecoration(labelText: "Method"),
              ),
              // Only show Low and High thresholds if Sobel is selected
              if (selectedMethod == 'canny') ...[
                TextFormField(
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a low value';
                    }
                    return null;
                  },

                  controller: lowController,
                  decoration: const InputDecoration(labelText: "Low"),
                  keyboardType: TextInputType.number,
                ),
                TextFormField(
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a high value';
                    }
                    return null;
                  },
                  controller: highController,
                  decoration: const InputDecoration(labelText: "High"),
                  keyboardType: TextInputType.number,
                ),
              ],
              const SizedBox(height: 10),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 84),
                child: ElevatedButton(
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.all(Color(0xff1751ab)),
                  ),
                  onPressed: _uploadImage,
                  child: const Text(
                    "Upload & Process",
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 10),
            if (_processedImageBytes != null)
              Column(
                children: [
                  Center(
                    child: const Text(
                      "Processed Image",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 28,
                      ),
                    ),
                  ),
                  SizedBox(height: 10),
                  Image.memory(_processedImageBytes!, height: 200),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

            //   Center(
            //     child: const Text(
            //       "Processed Image",
            //       style: TextStyle(fontWeight: FontWeight.bold, fontSize: 28),
            //     ),
            //   ),
            // SizedBox(height: 10),





























  //            Future<void> _uploadImage() async {
  //   if (_image == null) {
  //     _showMessage('No image selected');
  //     return;
  //   }

  //   try {
  //     var request = http.MultipartRequest(
  //       'POST',
  //       // غيّر الـ IP هنا إلى IP جهازك اللي عليه Django server
  //       Uri.parse('http://10.0.2.2:8000/api/process-image/'),
  //     );

  //     request.files.add(
  //       await http.MultipartFile.fromPath('image', _image!.path),
  //     );

  //     request.fields.addAll({
  //       'method': methodController.text,
  //       'low': lowController.text,
  //       'high': highController.text,
  //     });

  //     print('Sending request to server...');
  //     var response = await request.send();

  //     print('Response status: ${response.statusCode}');
  //     final respStr = await response.stream.bytesToString();
  //     print('Response body: $respStr');

  //     if (response.statusCode == 200) {
  //       final decoded = jsonDecode(respStr);
  //       if (decoded.containsKey('processed_image')) {
  //         setState(() {
  //           _processedImageBytes = base64Decode(decoded['processed_image']);
  //         });
  //         _showMessage('Image processed successfully!');
  //       } else {
  //         _showMessage('No processed image returned.');
  //       }
  //     } else {
  //       _showMessage('Failed: ${response.statusCode}');
  //     }
  //   } catch (e) {
  //     _showMessage('Error occurred: $e');
  //   }
  // }

