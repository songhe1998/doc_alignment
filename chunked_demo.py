#!/usr/bin/env python3
"""
Demo script for the chunked document alignment system.
This demonstrates how to use the chunked approach for aligning long documents.
"""

import os
from dotenv import load_dotenv
from chunked_alignment import ChunkedDocumentAligner

def create_sample_long_documents():
    """Create sample long legal documents for demonstration."""
    
    original_doc = """
**1. DEFINITIONS**

1.1 **"Software"** means the proprietary software application developed by Licensor, including all updates, modifications, and derivative works thereof.

1.2 **"Licensee"** means the individual or entity that has been granted a license to use the Software under the terms of this Agreement.

1.3 **"License"** means the non-exclusive, non-transferable right to use the Software in accordance with the terms and conditions set forth herein.

1.4 **"Documentation"** means all written materials, user manuals, technical specifications, and other materials provided by Licensor in connection with the Software.

1.5 **"Intellectual Property Rights"** means all patents, copyrights, trademarks, trade secrets, and other proprietary rights in and to the Software and Documentation.

**2. GRANT OF LICENSE**

2.1 Subject to the terms and conditions of this Agreement, Licensor hereby grants to Licensee a limited, non-exclusive, non-transferable license to use the Software solely for Licensee's internal business purposes.

2.2 The License granted hereunder is personal to Licensee and may not be assigned, sublicensed, or otherwise transferred without the prior written consent of Licensor.

2.3 Licensee may install the Software on up to five (5) computers owned or controlled by Licensee, provided that such computers are used solely for Licensee's internal business purposes.

2.4 Licensee may make one (1) backup copy of the Software for archival purposes only. Such backup copy must contain all copyright and proprietary notices contained in the original Software.

**3. RESTRICTIONS**

3.1 Licensee shall not, and shall not permit any third party to: (a) copy, modify, adapt, alter, translate, or create derivative works of the Software; (b) reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code of the Software; (c) rent, lease, lend, sell, sublicense, or otherwise transfer the Software to any third party; (d) remove, alter, or obscure any proprietary notices or labels on the Software.

3.2 Licensee acknowledges that the Software contains valuable trade secrets and proprietary information of Licensor and agrees to maintain the confidentiality thereof.

3.3 Licensee shall not use the Software for any unlawful or prohibited purpose or in any manner that could damage, disable, overburden, or impair any Licensor servers or networks.

**4. PAYMENT TERMS**

4.1 In consideration for the License granted hereunder, Licensee shall pay to Licensor the license fees set forth in Schedule A attached hereto.

4.2 All payments shall be due within thirty (30) days of the date of invoice and shall be made in the currency specified in Schedule A.

4.3 Any amounts not paid when due shall bear interest at the rate of one and one-half percent (1.5%) per month from the due date until paid in full.

4.4 Licensee shall be responsible for all taxes, duties, and other governmental charges imposed on the License or the Software, excluding taxes based on Licensor's income.

**5. SUPPORT AND MAINTENANCE**

5.1 Licensor shall provide technical support for the Software during normal business hours (9:00 AM to 5:00 PM, Monday through Friday) for a period of one (1) year from the date of this Agreement.

5.2 Support shall include assistance with installation, configuration, and basic troubleshooting of the Software.

5.3 Licensor shall provide updates and bug fixes for the Software at no additional cost during the support period.

5.4 Support does not include customization, training, or assistance with third-party software or hardware.

**6. WARRANTIES AND DISCLAIMERS**

6.1 Licensor warrants that the Software will substantially conform to the Documentation for a period of ninety (90) days from the date of delivery.

6.2 Licensor's sole obligation and Licensee's exclusive remedy for any breach of the foregoing warranty shall be, at Licensor's option, to repair or replace the Software or refund the license fees paid.

6.3 EXCEPT AS EXPRESSLY SET FORTH HEREIN, THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

6.4 LICENSOR SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, OR USE, ARISING OUT OF OR RELATING TO THIS AGREEMENT OR THE SOFTWARE.

**7. TERMINATION**

7.1 This Agreement shall commence on the date hereof and shall continue in effect until terminated in accordance with the provisions hereof.

7.2 Either party may terminate this Agreement immediately upon written notice if the other party breaches any material term or condition hereof and fails to cure such breach within thirty (30) days after written notice thereof.

7.3 Upon termination of this Agreement, Licensee shall immediately cease all use of the Software and shall return or destroy all copies of the Software and Documentation in its possession.

7.4 The provisions of Sections 3, 6, 8, and 9 shall survive termination of this Agreement.

**8. INTELLECTUAL PROPERTY**

8.1 Licensor retains all right, title, and interest in and to the Software and Documentation, including all Intellectual Property Rights therein.

8.2 Licensee acknowledges that the Software and Documentation are proprietary to Licensor and contain valuable trade secrets.

8.3 Licensee shall not challenge Licensor's ownership of the Software or Documentation or any Intellectual Property Rights therein.

**9. GENERAL PROVISIONS**

9.1 This Agreement constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous agreements, understandings, and communications.

9.2 This Agreement may not be modified except by a written instrument signed by both parties.

9.3 This Agreement shall be governed by and construed in accordance with the laws of the State of California, without regard to its conflict of laws principles.

9.4 Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration in accordance with the rules of the American Arbitration Association.

9.5 If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall remain in full force and effect.
"""

    variant_doc = """
**1. SCOPE AND PURPOSE**

1.1 **"Application"** refers to the comprehensive software solution created by the Provider, encompassing all versions, enhancements, and related components.

1.2 **"Client"** denotes the organization or individual who has obtained authorization to utilize the Application pursuant to this Contract.

1.3 **"Authorization"** represents the limited, revocable permission to access and use the Application subject to the stipulations contained herein.

1.4 **"Materials"** includes all accompanying documentation, guides, specifications, and supplementary resources provided by the Provider.

1.5 **"Proprietary Assets"** encompasses all copyrights, patents, trademarks, trade secrets, and other intellectual property associated with the Application and Materials.

**2. AUTHORIZATION GRANT**

2.1 In accordance with the terms of this Contract, Provider hereby authorizes Client to utilize the Application exclusively for Client's operational requirements.

2.2 This Authorization is specific to Client and cannot be transferred, assigned, or sublicensed to any third party without Provider's explicit written approval.

2.3 Client is permitted to deploy the Application on a maximum of ten (10) workstations under Client's direct control, provided such usage aligns with Client's business objectives.

2.4 Client may create a single archival copy of the Application for backup purposes, ensuring all proprietary markings and notices are preserved.

**3. USAGE LIMITATIONS**

3.1 Client agrees to refrain from, and to prevent any third party from: (a) reproducing, altering, adapting, or creating derivative works from the Application; (b) attempting to reverse engineer, decompile, or extract source code; (c) leasing, selling, or transferring the Application to unauthorized parties; (d) removing or modifying any proprietary notices or identifiers.

3.2 Client recognizes that the Application contains confidential information and proprietary technology of Provider and commits to maintaining such confidentiality.

3.3 Client shall not employ the Application for any illegal activities or in ways that could harm Provider's infrastructure or systems.

**4. COMPENSATION AND FEES**

4.1 As consideration for the Authorization granted herein, Client shall remit payment to Provider according to the fee schedule detailed in Appendix B.

4.2 Payment is due within forty-five (45) days of invoice receipt and must be made in the specified currency.

4.3 Overdue amounts will incur interest charges at the rate of two percent (2.0%) per month from the due date until settlement.

4.4 Client is responsible for all applicable taxes and governmental fees related to the Authorization, except for income taxes based on Provider's earnings.

**5. TECHNICAL ASSISTANCE**

5.1 Provider will furnish technical support for the Application during standard business hours (8:00 AM to 6:00 PM, Monday through Friday) for a duration of two (2) years from the Contract execution date.

5.2 Support encompasses help with deployment, setup, and resolution of technical issues with the Application.

5.3 Provider will deliver software updates and corrections at no extra charge during the support term.

5.4 Support services do not cover custom development, user training, or integration with external systems.

**6. GUARANTEES AND LIMITATIONS**

6.1 Provider guarantees that the Application will function substantially as described in the Materials for a period of one hundred twenty (120) days from delivery.

6.2 Provider's exclusive remedy for warranty breaches shall be, at Provider's discretion, to correct defects, provide replacement software, or refund applicable fees.

6.3 THE APPLICATION IS FURNISHED "AS AVAILABLE" WITHOUT ANY WARRANTIES, WHETHER EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT.

6.4 PROVIDER SHALL NOT BE RESPONSIBLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOSS OF REVENUE, DATA, OR BUSINESS OPPORTUNITIES.

**7. CONTRACT TERMINATION**

7.1 This Contract becomes effective upon execution and remains valid until terminated according to its provisions.

7.2 Either party may immediately terminate this Contract by written notice if the other party materially breaches any term and fails to remedy such breach within forty-five (45) days of notice.

7.3 Upon Contract termination, Client must immediately discontinue all Application usage and return or delete all copies of the Application and Materials.

7.4 Sections 3, 6, 8, and 9 provisions shall remain in effect following Contract termination.

**8. PROPRIETARY RIGHTS**

8.1 Provider maintains complete ownership of the Application and Materials, including all associated Proprietary Assets.

8.2 Client acknowledges the proprietary nature of the Application and Materials and their status as confidential information.

8.3 Client shall not dispute Provider's ownership rights in the Application, Materials, or related Proprietary Assets.

**9. MISCELLANEOUS TERMS**

9.1 This Contract represents the complete understanding between the parties regarding the subject matter and replaces all prior agreements and communications.

9.2 Modifications to this Contract require written consent from both parties.

9.3 This Contract shall be interpreted under the laws of the State of New York, excluding conflict of law principles.

9.4 Disputes related to this Contract shall be resolved through binding arbitration under the Commercial Arbitration Rules of the American Arbitration Association.

9.5 If any Contract provision is deemed invalid, the remaining terms shall continue to be enforceable.

**10. ADDITIONAL PROVISIONS**

10.1 **Data Protection**: Client agrees to implement reasonable security measures to protect any data processed by the Application.

10.2 **Compliance**: Client shall ensure compliance with all applicable laws and regulations when using the Application.

10.3 **Indemnification**: Client agrees to indemnify Provider against any claims arising from Client's use of the Application in violation of this Contract.
"""
    
    return original_doc, variant_doc

def main():
    """Main demo function."""
    print("🚀 Chunked Document Alignment Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables.")
        print("Please create a .env file with your OpenAI API key.")
        return
    
    # Create sample documents
    print("\n📄 Creating sample long legal documents...")
    original_doc, variant_doc = create_sample_long_documents()
    
    print(f"Original document: {len(original_doc.split())} words")
    print(f"Variant document: {len(variant_doc.split())} words")
    
    # Initialize aligner with smaller chunks for demo
    print("\n🔧 Initializing chunked aligner...")
    aligner = ChunkedDocumentAligner(
        api_key=api_key,
        chunk_size=500,  # Smaller chunks for demo
        overlap_size=100
    )
    
    # Run alignment
    print("\n🚀 Running chunked alignment...")
    result = aligner.run_chunked_alignment(original_doc, variant_doc)
    
    # Display final summary
    print(f"\n🎉 Demo Complete!")
    print(f"📊 Results Summary:")
    print(f"   • Original chunks: {len(result.original_chunks)}")
    print(f"   • Variant chunks: {len(result.variant_chunks)}")
    print(f"   • Alignments found: {len(result.chunk_alignments)}")
    print(f"   • Total words processed: {result.total_words_processed:,}")
    print(f"   • Processing time: {result.processing_time:.2f}s")
    print(f"   • Throughput: {result.total_words_processed/result.processing_time:.1f} words/sec")

if __name__ == "__main__":
    main()
