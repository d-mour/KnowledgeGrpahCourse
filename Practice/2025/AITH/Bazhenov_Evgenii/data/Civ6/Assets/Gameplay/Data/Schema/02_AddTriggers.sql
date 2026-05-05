-- Add triggers.
CREATE TRIGGER OnKindInsert AFTER INSERT ON Kinds BEGIN UPDATE Kinds SET Hash = Make_Hash(Kind) Where Kind = New.Kind; END;
CREATE TRIGGER OnTypeInsert AFTER INSERT ON Types BEGIN UPDATE Types SET Hash = Make_Hash(Type) Where Type = New.Type; END;
CREATE TRIGGER OnDeleteGameCapabilityDependency AFTER DELETE ON GameCapabilityDependencies BEGIN DELETE FROM GameCapabilities where GameCapability = OLD.GameCapability; END;