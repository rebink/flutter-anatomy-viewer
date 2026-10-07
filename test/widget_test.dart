import 'package:anatomy_viewer/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Demo detail navigation preserves organ, severity and disclaimer',
      (tester) async {
    await tester.pumpWidget(MaterialApp(home: Builder(builder: (context) {
      return Scaffold(
          body: TextButton(
        onPressed: () => Navigator.push<void>(
            context,
            MaterialPageRoute(
              builder: (_) => FindingDetails(finding: demoFindings.first),
            )),
        child: const Text('View details'),
      ));
    })));
    await tester.tap(find.text('View details'));
    await tester.pumpAndSettle();
    expect(find.text('Left lung'), findsOneWidget);
    expect(find.text('Danger · DEMO'), findsOneWidget);
    expect(find.textContaining('No report is attached.'), findsOneWidget);
    expect(find.textContaining('fictional data'), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.text('View details'), findsOneWidget);
  });
}
