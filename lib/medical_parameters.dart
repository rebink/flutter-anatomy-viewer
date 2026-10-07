import 'package:flutter/material.dart';

/// Navigation metadata, not the enabled MedicalParameter catalog.
const bodySystems = <String, ({String name, List<String> organs, String note})>{
  'cardiovascular': (
    name: 'Heart and blood vessels',
    organs: ['heart'],
    note:
        'Includes device measurements, labs, report extraction and estimated cardiovascular risk. No vascular mesh is included.',
  ),
  'respiratory': (
    name: 'Lungs and respiratory system',
    organs: ['lung_left', 'lung_right', 'airway'],
    note:
        'VO2 max describes cardiorespiratory fitness, not a lung-specific diagnosis.',
  ),
  'sleep_stress': (
    name: 'Brain, nervous system, sleep and stress',
    organs: ['brain'],
    note:
        'Sleep, stress and recovery indicators are not direct measurements of brain function.',
  ),
  'metabolic': (
    name: 'Pancreas, blood sugar and metabolism',
    organs: ['pancreas'],
    note:
        'Includes glucose, CGM summaries and metabolic estimates. Insulin catalog availability is unconfirmed.',
  ),
  'liver': (
    name: 'Liver',
    organs: ['liver'],
    note:
        'Platelets may also relate to blood and immunity. Bilirubin extraction does not establish total, direct or indirect subtypes.',
  ),
  'renal': (
    name: 'Kidneys, electrolytes and fluid balance',
    organs: ['kidney_left', 'kidney_right'],
    note:
        'GFR categorization alone does not establish an enabled parameter or a supported eGFR calculation.',
  ),
  'thyroid': (
    name: 'Thyroid',
    organs: [],
    note:
        'No thyroid mesh is included. T3/T4 extraction does not establish separate free and total parameters.',
  ),
  'blood_immune': (
    name: 'Blood, immune system and inflammation',
    organs: [],
    note:
        'System-wide; no dedicated mesh. CRP and hsCRP are separate parameters. WBC differential does not imply a fixed cell-type list.',
  ),
  'body_composition': (
    name: 'Muscles, bones and body composition',
    organs: [],
    note:
        'No muscle or skeleton meshes are included. Device bone mass is not a bone-density scan result.',
  ),
  'temperature': (
    name: 'Skin and body temperature',
    organs: [],
    note: 'System-wide; the body shell is illustrative, not a skin assessment.',
  ),
  'digestive': (
    name: 'Gut and digestive system',
    organs: ['stomach', 'esophagus', 'small_intestine', 'large_intestine'],
    note:
        'Rome IV and Manning are questionnaire-based assessments. No fixed stool-test or microbiome panel is established.',
  ),
  'fitness': (
    name: 'Whole-body fitness, energy and recovery',
    organs: [],
    note:
        'System-wide wellness and performance indicators, not strictly medical tests.',
  ),
};

enum ParameterEvidence {
  measurement('Measurement / device or profile data'),
  laboratory('Blood-test parameter'),
  reportExtraction('Report-extraction support'),
  calculated('Calculated assessment'),
  estimate('Estimate / face scan'),
  questionnaire('Questionnaire assessment'),
  unconfirmed('Limited or unconfirmed evidence');

  const ParameterEvidence(this.label);
  final String label;
}

/// Host adapter output. Preserve database IDs; do not infer enablement from names.
/// System membership must come from a reviewed mapping and may be many-to-many.
class MedicalParameter {
  MedicalParameter({
    required this.id,
    required this.name,
    required this.enabled,
    required this.evidence,
    required List<String> systemIds,
    this.sourceNote = '',
  }) : systemIds = List.unmodifiable(systemIds) {
    if (id.trim().isEmpty || name.trim().isEmpty) {
      throw ArgumentError('MedicalParameter requires a non-empty ID and name');
    }
  }

  final String id;
  final String name;
  final bool enabled;
  final ParameterEvidence evidence;
  final List<String> systemIds;
  final String sourceNote;
}

class MedicalParametersPage extends StatelessWidget {
  const MedicalParametersPage({
    super.key,
    required this.parameters,
    this.organ,
  });

  /// Null means not connected; an empty list means a loaded, empty catalog.
  final List<MedicalParameter>? parameters;
  final String? organ;

  @override
  Widget build(BuildContext context) {
    final enabled = parameters?.where((p) => p.enabled).toList() ?? [];
    final unmapped = enabled
        .where((p) =>
            p.systemIds.isEmpty ||
            p.systemIds.any((id) => !bodySystems.containsKey(id)))
        .toList();
    Widget parameterTile(MedicalParameter p) => ListTile(
          title: Text(p.name),
          subtitle: Text([
            p.evidence.label,
            if (p.sourceNote.isNotEmpty) p.sourceNote,
            'Device availability and patient results are not established by catalog enablement.',
          ].join('\n')),
        );
    return Scaffold(
      appBar: AppBar(title: const Text('Body systems and parameters')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        Text(parameters == null
            ? 'MedicalParameter catalog not connected. No enabled parameters are assumed.'
            : '${enabled.length} enabled catalog entries. Catalog metadata only, not patient results.'),
        const SizedBox(height: 12),
        for (final entry in bodySystems.entries)
          if (organ == null || entry.value.organs.contains(organ))
            Card(
              child: ExpansionTile(
                title: Text(entry.value.name),
                subtitle: Text(entry.value.organs.isEmpty
                    ? 'List only - no dedicated 3D region'
                    : 'Related anatomy, not a diagnosis'),
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(entry.value.note),
                  ),
                  for (final p in enabled)
                    if (p.systemIds.contains(entry.key)) parameterTile(p),
                  if (!enabled.any((p) => p.systemIds.contains(entry.key)))
                    const ListTile(
                        title: Text(
                            'No enabled entries supplied for this system.')),
                ],
              ),
            ),
        if (organ == null && unmapped.isNotEmpty)
          Card(
              child: ExpansionTile(
            title: const Text('Unmapped parameters'),
            subtitle: const Text('Preserved without guessing a body region'),
            children: unmapped.map(parameterTile).toList(),
          )),
        if (organ != null &&
            !bodySystems.values.any((s) => s.organs.contains(organ)))
          const Text(
              'No reviewed system mapping for this organ. Browse all systems for the full catalog.'),
      ]),
    );
  }
}
