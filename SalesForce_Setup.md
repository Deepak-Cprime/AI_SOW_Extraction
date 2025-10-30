# Complete Salesforce PDF Extraction Integration Guide
## From Scratch Setup Documentation

This guide will help you set up the complete PDF extraction integration in a **brand new Salesforce org**.

---

## **Table of Contents**
1. [Prerequisites](#prerequisites)
2. [Step 1: Remote Site Settings](#step-1-remote-site-settings)
3. [Step 2: Create Apex Class](#step-2-create-apex-class)
4. [Step 3: Create Apex Trigger](#step-3-create-apex-trigger)
5. [Step 4: Setup Debug Logs](#step-4-setup-debug-logs)
6. [Step 5: Create Test Opportunity](#step-5-create-test-opportunity)
7. [Step 6: Test the Integration](#step-6-test-the-integration)
8. [Step 7: View Results](#step-7-view-results)
9. [Optional Enhancements](#optional-enhancements)
10. [Troubleshooting](#troubleshooting)

---

## **Prerequisites**

Before starting, ensure you have:
- ✅ A Salesforce Developer Edition org (or any Salesforce org)
- ✅ System Administrator access
- ✅ Your Flask API deployed and running at: `https://ai-sow-extraction.onrender.com`
- ✅ The API endpoint `/extract-sow-base64` accepting JSON with fields: `filename` and `file_content` (base64)

---

## **Step 1: Remote Site Settings**

Allow Salesforce to make HTTP callouts to your API.

### **Instructions:**

1. Click the **gear icon** ⚙️ (top right) → **Setup**
2. In the **Quick Find** box (left side), type: `Remote Site Settings`
3. Click **Remote Site Settings**
4. Click **New Remote Site**
5. Fill in the form:
   ```
   Remote Site Name: AI_SOW_Extraction_API
   Remote Site URL: https://ai-sow-extraction.onrender.com
   Description: API endpoint for PDF SOW extraction
   Active: ✅ (checked)
   ```
6. Click **Save**

### **Screenshot Reference:**
You should see your new remote site listed with status "Active"

---

## **Step 2: Create Apex Class**

Create the class that handles PDF extraction and API communication.

### **Instructions:**

1. In **Setup**, type in Quick Find: `Apex Classes`
2. Click **Apex Classes**
3. Click **New**
4. **Delete all default code** and paste the following:

```apex
public class OpportunityPDFSender {
    
    /**
     * Sends PDF from Opportunity to external API for extraction
     * This method runs asynchronously after Opportunity stage changes to Closed
     * @param opportunityId The ID of the Opportunity containing the PDF
     */
    @future(callout=true)
    public static void sendPDFToAPI(Id opportunityId) {
        try {
            System.debug('=== Starting PDF Extraction Process ===');
            System.debug('Opportunity ID: ' + opportunityId);
            
            // Step 1: Get ContentDocumentLinks for this Opportunity
            List<ContentDocumentLink> cdLinks = [
                SELECT ContentDocumentId 
                FROM ContentDocumentLink 
                WHERE LinkedEntityId = :opportunityId
                LIMIT 100
            ];
            
            if (cdLinks.isEmpty()) {
                System.debug('❌ No files linked to this Opportunity');
                return;
            }
            
            System.debug('Found ' + cdLinks.size() + ' linked documents');
            
            // Step 2: Get the document IDs
            Set<Id> contentDocIds = new Set<Id>();
            for (ContentDocumentLink cdl : cdLinks) {
                contentDocIds.add(cdl.ContentDocumentId);
            }
            
            // Step 3: Get PDF files from the Files section
            List<ContentVersion> pdfFiles = [
                SELECT Id, VersionData, Title, FileExtension
                FROM ContentVersion 
                WHERE ContentDocumentId IN :contentDocIds 
                AND FileExtension = 'pdf'
                AND IsLatest = true
                ORDER BY CreatedDate DESC
                LIMIT 1
            ];
            
            if (pdfFiles.isEmpty()) {
                System.debug('❌ No PDF files found for Opportunity: ' + opportunityId);
                return;
            }
            
            ContentVersion pdfFile = pdfFiles[0];
            String filename = pdfFile.Title + '.pdf';
            
            System.debug('✅ Found PDF: ' + filename);
            
            // Step 4: Prepare HTTP request
            Http http = new Http();
            HttpRequest request = new HttpRequest();
            
            // API endpoint - update this if your endpoint changes
            request.setEndpoint('https://ai-sow-extraction.onrender.com/extract-sow-base64');
            request.setMethod('POST');
            request.setTimeout(120000); // 2 minutes timeout
            request.setHeader('Content-Type', 'application/json');
            
            // Step 5: Build JSON payload with base64 encoded PDF
            Map<String, String> jsonBody = new Map<String, String>{
                'filename' => filename,
                'file_content' => EncodingUtil.base64Encode(pdfFile.VersionData)
            };
            
            String jsonString = JSON.serialize(jsonBody);
            request.setBody(jsonString);
            
            System.debug('=== Sending PDF to API ===');
            System.debug('Endpoint: ' + request.getEndpoint());
            System.debug('Filename: ' + filename);
            System.debug('JSON Preview: ' + jsonString.substring(0, Math.min(200, jsonString.length())) + '...');
            
            // Step 6: Send request to API
            HttpResponse response = http.send(request);
            
            // Step 7: Log and process response
            System.debug('=== API Response ===');
            System.debug('Status Code: ' + response.getStatusCode());
            System.debug('Response Body: ' + response.getBody());
            
            if (response.getStatusCode() == 200 || response.getStatusCode() == 201) {
                System.debug('✅ PDF sent successfully to API!');
                
                try {
                    // Parse the JSON response
                    Map<String, Object> result = (Map<String, Object>)JSON.deserializeUntyped(response.getBody());
                    System.debug('Extracted Data: ' + result);
                    
                    // Optional: Store extracted content back to Opportunity
                    // Uncomment the lines below after creating the custom field (see Optional Enhancements)
                    /*
                    String extractedContent = JSON.serializePretty(result);
                    Opportunity opp = new Opportunity(
                        Id = opportunityId,
                        Extracted_SOW_Content__c = extractedContent
                    );
                    update opp;
                    System.debug('✅ Saved extracted content to Opportunity');
                    */
                    
                } catch (Exception parseEx) {
                    System.debug('⚠️ Could not parse JSON response: ' + parseEx.getMessage());
                    System.debug('Raw Response: ' + response.getBody());
                }
            } else {
                System.debug('❌ Error sending PDF. Status: ' + response.getStatusCode());
                System.debug('Error Response: ' + response.getBody());
            }
            
        } catch (Exception e) {
            System.debug('❌ Exception occurred: ' + e.getMessage());
            System.debug('Stack Trace: ' + e.getStackTraceString());
        }
    }
}
```

5. Click **Save**

### **What This Class Does:**
- Retrieves PDF files attached to an Opportunity
- Converts the PDF to base64 encoding
- Sends it to your Flask API as JSON
- Logs all steps for debugging
- Handles errors gracefully

---

## **Step 3: Create Apex Trigger**

Create a trigger that automatically calls the Apex class when an Opportunity is closed.

### **Instructions:**

#### **Option A: Via Developer Console (Recommended)**

1. Click the **gear icon** ⚙️ → **Developer Console**
2. Click **File** → **New** → **Apex Trigger**
3. In the dialog:
   ```
   Name: OpportunityPDFTrigger
   sObject: Opportunity
   ```
4. Click **Submit**
5. **Delete all default code** and paste:

```apex
/**
 * Trigger to automatically send PDF to extraction API when Opportunity closes
 * Fires when: Opportunity Stage changes to 'Closed Won' or 'Closed Lost'
 */
trigger OpportunityPDFTrigger on Opportunity (after update) {
    
    // Loop through all updated Opportunities
    for (Opportunity opp : Trigger.new) {
        
        // Get the old version of the Opportunity to check what changed
        Opportunity oldOpp = Trigger.oldMap.get(opp.Id);
        
        // Check if the Stage changed AND it's now a closed stage
        Boolean stageChanged = (opp.StageName != oldOpp.StageName);
        Boolean isClosedWon = (opp.StageName == 'Closed Won');
        Boolean isClosedLost = (opp.StageName == 'Closed Lost');
        
        if (stageChanged && (isClosedWon || isClosedLost)) {
            System.debug('Opportunity closed - triggering PDF extraction for: ' + opp.Id);
            
            // Call the async method to send PDF to API
            OpportunityPDFSender.sendPDFToAPI(opp.Id);
        }
    }
}
```

6. Press **Ctrl+S** (or **Cmd+S** on Mac) to save

#### **Option B: Via Setup (If Developer Console doesn't work)**

1. In **Setup**, type: `Apex Triggers`
2. If you see a "New" button, click it
3. If not, you must use Developer Console (Option A above)

### **What This Trigger Does:**
- Monitors all Opportunity updates
- Detects when Stage changes to "Closed Won" or "Closed Lost"
- Automatically calls the PDF extraction process

---

## **Step 4: Setup Debug Logs**

Enable debug logging to see what's happening.

### **Instructions:**

1. In **Setup**, type: `Debug Logs`
2. Click **Debug Logs**
3. Click **New** button

#### **4.1: Create Debug Level (if needed)**

If you need to create a debug level:

1. Look for **Debug Level** field
2. Click the **lookup icon** (magnifying glass)
3. If no debug levels exist, click **New** or **Create New Debug Level**
4. Fill in:
   ```
   Debug Level Name: SFDC_DevConsole
   
   Database: FINEST
   Workflow: FINEST
   Validation: INFO
   Callout: FINEST  ← IMPORTANT for seeing API calls!
   Apex Code: FINEST
   Apex Profiling: INFO
   Visualforce: INFO
   System: DEBUG
   Wave: INFO
   NBA: INFO
   All others: INFO
   ```
5. Click **Save**

#### **4.2: Create Trace Flag**

1. Back on the Debug Logs page, click **New**
2. Fill in:
   ```
   Traced Entity Type: User
   Traced Entity Name: [Search and select YOUR username]
   Start Date: [Today's date - auto-filled]
   Expiration Date: [Tomorrow or a few days from now]
   Debug Level: SFDC_DevConsole (or the one you just created)
   ```
3. Click **Save**

### **What This Does:**
- Captures detailed logs of all operations
- Logs will be available for viewing for the duration specified
- **CALLOUT: FINEST** is critical for seeing API request/response

---

## **Step 5: Create Test Opportunity**

Create an Opportunity to test the integration.

### **Instructions:**

1. Click the **App Launcher** (9 dots, top-left)
2. Search for and click **Opportunities**
3. Click **New** button
4. Fill in the required fields:
   ```
   Opportunity Name: PDF Extraction Test Opportunity
   Close Date: [Any future date, e.g., 12/31/2025]
   Stage: Prospecting (or any early stage)
   Amount: 50000 (optional)
   ```
5. Click **Save**

### **5.1: Upload a PDF to the Opportunity**

1. On the Opportunity record page, scroll down to the **Files** section
2. Click **Upload Files** button (or drag and drop)
3. Select your PDF file (the SOW document you want to extract)
4. Wait for upload to complete
5. Verify the PDF appears in the Files section

### **Important Notes:**
- The PDF must be in the **Files** section (not Notes & Attachments)
- Make sure it's a `.pdf` file
- File should be under 10MB for best performance

---

## **Step 6: Test the Integration**

Now let's trigger the PDF extraction process.

### **Method 1: Change Opportunity Stage (Real Scenario)**

1. On your Opportunity record, click **Edit**
2. Change **Stage** to: `Closed Won`
3. Click **Save**
4. Wait 5-10 seconds for the async process to complete

### **Method 2: Manual Test via Developer Console**

1. Copy your Opportunity ID:
   - From the URL: `https://your-org.lightning.force.com/lightning/r/Opportunity/006XXXXXXXXXXXXXXX/view`
   - The ID is the part after `/Opportunity/` (starts with `006`)

2. Open **Developer Console** (gear icon → Developer Console)
3. Click **Debug** → **Open Execute Anonymous Window**
4. Paste this code (replace with your Opportunity ID):

```apex
// Replace this ID with your actual Opportunity ID
Id oppId = '006XXXXXXXXXXXXXXX';

// Trigger the PDF extraction
OpportunityPDFSender.sendPDFToAPI(oppId);
```

5. Check the **Open Log** checkbox ✅
6. Click **Execute**
7. The log will open automatically at the bottom

---

## **Step 7: View Results**

Check if the integration worked successfully.

### **7.1: View Debug Logs**

1. Go to **Setup** → **Debug Logs**
2. You should see **2 new logs**:
   - One for the trigger execution
   - One for the API callout (Operation: `FutureHandler`)

3. Click **View** on the log with **Operation** = `FutureHandler`
4. Press **Ctrl+F** and search for these key phrases:

#### **What to Look For:**

✅ **Success Indicators:**
```
✅ Found PDF: [filename].pdf
=== Sending PDF to API ===
Status Code: 200
✅ PDF sent successfully to API!
Extracted Data: {success=true, extracted_content={...}}
```

❌ **Error Indicators:**
```
❌ No files linked to this Opportunity
❌ No PDF files found
Status Code: 404 (or 422, 500)
❌ Error sending PDF
```

### **7.2: View Flask API Logs (Optional)**

1. Go to **https://dashboard.render.com**
2. Click your service: **ai-sow-extraction**
3. Click **Logs** tab
4. Look for:
   ```
   INFO: 155.226.153.254:0 - "POST /extract-sow-base64 HTTP/1.1" 200 OK
   ```

---

## **Optional Enhancements**

### **Enhancement 1: Store Extracted Content on Opportunity**

Create a custom field to save the API response.

#### **Step 1: Create Custom Field**

1. **Setup** → **Object Manager** → **Opportunity**
2. Click **Fields & Relationships**
3. Click **New**
4. Select **Text Area (Long)**
5. Click **Next**
6. Fill in:
   ```
   Field Label: Extracted SOW Content
   Field Name: Extracted_SOW_Content
   Length: 131072 (maximum)
   # Visible Lines: 10
   ```
7. Click **Next** → **Next** → **Save**

#### **Step 2: Update Apex Class**

1. Go to **Setup** → **Apex Classes**
2. Click **Edit** next to `OpportunityPDFSender`
3. Find the commented section around line 75:
   ```apex
   // Optional: Store extracted content back to Opportunity
   // Uncomment the lines below after creating the custom field
   ```
4. **Uncomment** (remove `//` and `/* */`) the code below it:
   ```apex
   String extractedContent = JSON.serializePretty(result);
   Opportunity opp = new Opportunity(
       Id = opportunityId,
       Extracted_SOW_Content__c = extractedContent
   );
   update opp;
   System.debug('✅ Saved extracted content to Opportunity');
   ```
5. Click **Save**

#### **Step 3: Add Field to Page Layout**

1. **Setup** → **Object Manager** → **Opportunity**
2. Click **Page Layouts**
3. Click **Opportunity Layout** (or your layout name)
4. Drag **Extracted SOW Content** field onto the layout
5. Click **Save**

Now the extracted content will be saved directly on the Opportunity record!

---

### **Enhancement 2: Create Manual Extraction Button**

Add a button to extract PDF on-demand instead of only on stage change.

#### **Coming soon - let me know if you need this!**

---

### **Enhancement 3: Email Notification on Errors**

Get notified if extraction fails.

#### **Add to Apex Class (around line 115):**

```apex
} else {
    System.debug('❌ Error sending PDF. Status: ' + response.getStatusCode());
    
    // Send email notification
    Messaging.SingleEmailMessage mail = new Messaging.SingleEmailMessage();
    mail.setToAddresses(new String[] {'your-email@example.com'});
    mail.setSubject('PDF Extraction Failed - Opportunity ' + opportunityId);
    mail.setPlainTextBody('The PDF extraction failed with status code: ' + response.getStatusCode() + '\n\nError: ' + response.getBody());
    Messaging.sendEmail(new Messaging.SingleEmailMessage[] { mail });
}
```

---

## **Troubleshooting**

### **Problem: "Unauthorized endpoint"**

**Solution:**
- Check **Remote Site Settings**
- Verify URL is exactly: `https://ai-sow-extraction.onrender.com`
- No trailing slashes

---

### **Problem: "No PDF files found"**

**Solution:**
- Ensure PDF is in **Files** section (not Notes & Attachments)
- Check file extension is `.pdf`
- Verify file uploaded successfully

---

### **Problem: Status Code 404**

**Solution:**
- Check your Flask API is running: visit `https://ai-sow-extraction.onrender.com` in browser
- Verify endpoint is `/extract-sow-base64`
- Check Render logs for errors

---

### **Problem: Status Code 422**

**Solution:**
- Flask API expects fields named: `filename` and `file_content`
- Check your Flask code matches the JSON structure being sent
- View debug logs to see exact JSON being sent

---

### **Problem: Font warnings in Flask logs**

**Solution:**
- These are harmless warnings from PDF parsing libraries
- They don't affect extraction
- To suppress, add to Flask app.py:
  ```python
  import logging
  logging.getLogger('pdfminer').setLevel(logging.ERROR)
  ```

---

### **Problem: "Number of callouts: 0"**

**Solution:**
- Trigger didn't fire the API call
- Check trigger logic - Stage must change to "Closed Won" or "Closed Lost"
- Or use manual test method in Developer Console

---

## **Complete Integration Flow Summary**

```
1. User uploads PDF to Opportunity (Files section)
                    ↓
2. User changes Opportunity Stage to "Closed Won"
                    ↓
3. OpportunityPDFTrigger fires (after update)
                    ↓
4. Trigger calls OpportunityPDFSender.sendPDFToAPI()
                    ↓
5. Apex queries for PDF file from Files
                    ↓
6. PDF converted to Base64 string
                    ↓
7. JSON payload created: {filename, file_content}
                    ↓
8. HTTP POST to https://ai-sow-extraction.onrender.com/extract-sow-base64
                    ↓
9. Flask API receives, decodes, and extracts content
                    ↓
10. API returns JSON with extracted data (200 OK)
                    ↓
11. Salesforce logs response in Debug Logs
                    ↓
12. [Optional] Extracted content saved to Opportunity field
```

---

## **Quick Reference Commands**

### **Test Manually:**
```apex
Id oppId = '006XXXXXXXXXXXXXXX';
OpportunityPDFSender.sendPDFToAPI(oppId);
```

### **Check Apex Jobs:**
```
Setup → Apex Jobs
Look for: Method = OpportunityPDFSender.sendPDFToAPI
```

### **View Latest Log:**
```
Setup → Debug Logs → Click View on latest "FutureHandler"
Search for: "Status Code" or "Extracted Data"
```

---

## **Support & Next Steps**

✅ **Integration Complete!** Your Salesforce org is now set up to automatically extract PDF content when opportunities close.

**Questions?**
- Check Debug Logs first
- Review Troubleshooting section
- Test with Developer Console for immediate feedback

**Want to customize further?**
- Modify trigger to fire on different stage changes
- Add custom fields for specific extracted data
- Create reports on extracted content
- Build Flow automations based on extraction results

---

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Tested On:** Salesforce Developer Edition

---

This completes the full documentation! You can now set up this integration in any fresh Salesforce org by following these steps. 🚀