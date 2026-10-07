import 'package:anatomy_viewer/main.dart';
import 'package:anatomy_viewer/medical_parameters.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('All twelve systems use only available meshes', () {
    expect(bodySystems.length, 12);
    for (final system in bodySystems.values) {
      expect(system.organs.every(organNames.containsKey), isTrue);
    }
    expect(
        () => MedicalParameter(
            id: '',
            name: 'Invalid',
            enabled: true,
            evidence: ParameterEvidence.measurement,
            systemIds: []),
        throwsArgumentError);
  });

  testWidgets(
      'Catalog stays dynamic, separates CRP/hsCRP and preserves unknowns',
      (tester) async {
    MedicalParameter parameter(String id, List<String> systems,
            {bool enabled = true}) =>
        MedicalParameter(
            id: id,
            name: id,
            enabled: enabled,
            evidence: ParameterEvidence.reportExtraction,
            systemIds: systems);
    final parameters = [
      parameter('CRP', ['cardiovascular']),
      parameter('hsCRP', ['cardiovascular', 'blood_immune']),
      parameter('Future database entry', ['cardiovascular']),
      parameter('Disabled', ['cardiovascular'], enabled: false),
      parameter('Unknown mapping', ['future_system']),
      parameter('No mapping', []),
    ];
    await tester.pumpWidget(
        MaterialApp(home: MedicalParametersPage(parameters: parameters)));
    await tester.tap(find.text('Heart and blood vessels'));
    await tester.pumpAndSettle();
    expect(find.text('CRP'), findsOneWidget);
    expect(find.text('hsCRP'), findsOneWidget);
    expect(find.text('Future database entry'), findsOneWidget);
    expect(find.text('Disabled'), findsNothing);
    await tester.scrollUntilVisible(find.text('Unmapped parameters'), 500);
    await tester.tap(find.text('Unmapped parameters'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('No mapping'), 200);
    expect(find.text('Unknown mapping'), findsOneWidget);
    expect(find.text('No mapping'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Disconnected, empty and organ-filtered catalogs are explicit',
      (tester) async {
    await tester.pumpWidget(
        const MaterialApp(home: MedicalParametersPage(parameters: null)));
    expect(find.textContaining('catalog not connected'), findsOneWidget);
    await tester.pumpWidget(const MaterialApp(
        home: MedicalParametersPage(parameters: [], organ: 'lung_left')));
    expect(find.textContaining('0 enabled catalog entries'), findsOneWidget);
    expect(find.text('Lungs and respiratory system'), findsOneWidget);
    expect(find.text('Heart and blood vessels'), findsNothing);
  });
}
